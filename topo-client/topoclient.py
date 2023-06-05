import sys
import os
import common
import redisconn
import kafkaconn
import json
import socket
import time


class TopoClient:
    def __init__(self):
        common.parse_config()
        self.redisconn = redisconn.RedisConn()
        self.kafkaconn = kafkaconn.KafkaConn()
        self.nodes_library = set()
        self.edges_library = set()

    def get_local_host4(self) -> str:
        return common.LOCAL_IPV4_ADDR
        # return socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)[1][4][0]

    def get_local_host6(self) -> str:
        return common.LOCAL_IPV6_ADDR
        # return socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6)[1][4][0]

    def start(self):
        common.get_logger().info('Start')
        for msg in self.kafkaconn.cmd_consumer:
            self.process(msg.value)

    def process(self, msg: bytes):
        msg_dict = json.loads(msg)
        if self.get_local_host6() not in msg_dict.get('host', []):
            return
        common.get_logger().info('Processing Command: %s', msg_dict)
        if msg_dict['type'] == common.MSG_TYPE_TRACEROUTE4:
            self.traceroute(msg_dict, 4)
        elif msg_dict['type'] == common.MSG_TYPE_TRACEROUTE6:
            self.traceroute(msg_dict, 6)

    def traceroute(self, msg_dict: dict, ip_version: int = 4):
        common.get_logger().info('Starting Traceroute, IP Version = %d', ip_version)
        opr_id = msg_dict['opr_id']
        host = self.get_local_host4() if ip_version == 4 else self.get_local_host6()

        while True:
            target_str = self.redisconn.get(str(opr_id) + ':target')
            if target_str is not None and len(target_str) > 0:
                break
            time.sleep(10)

        self.redisconn.hset(str(opr_id) + ':status', host, 'P')
        common.get_logger().info('Status Redis Set to Processing')
        with open(common.YARRP_INPUT_DIR, 'w') as f:
            print(target_str, file=f)
        self.call_yarrp(opr_id, host, ip_version=ip_version)
        nodes, edges = self.parse_yarrp_output(opr_id, host)

        batch_size = 5000

        low = 0
        while low < len(nodes):
            res_dict = {
                'type': common.MSG_TYPE_TRACEROUTE4_RESULT if ip_version == 4 else common.MSG_TYPE_TRACEROUTE6_RESULT,
                'opr_id': opr_id,
                'host': host,
                'nodes': nodes[low: low + batch_size],
            }
            if low + batch_size >= len(nodes):
                res_dict['finished'] = 1
            self.kafkaconn.res(res_dict)
            low += batch_size
        common.get_logger().info('Traceroute Results of Nodes Sent')

        low = 0
        while low < len(edges):
            res_dict = {
                'type': common.MSG_TYPE_TRACEROUTE4_RESULT if ip_version == 4 else common.MSG_TYPE_TRACEROUTE6_RESULT,
                'opr_id': opr_id,
                'host': host,
                'edges': edges[low: low + batch_size],
            }
            if low + batch_size >= len(edges):
                res_dict['finished'] = 1
            self.kafkaconn.res(res_dict)
            low += batch_size
        common.get_logger().info('Traceroute Results of Edges Sent')

        self.redisconn.hset(str(opr_id) + ':status', host, 'F')
        common.get_logger().info('Status Redis Set to Finished')

        res_dict = {
            'type': common.MSG_TYPE_TRACEROUTE4_RESULT if ip_version == 4 else common.MSG_TYPE_TRACEROUTE6_RESULT,
            'opr_id': opr_id,
            'host': host,
            'node': nodes,
            'edges': edges,
        }
        file_name = 'output/%d-%s.json' % (opr_id, host)
        with open(file_name, 'w') as f:
            print(res_dict, file=f)

        common.get_logger().info('Results Saved Locally as %s' % file_name)

    def call_yarrp(self, opr_id: int, host: str, ip_version: int = 4, pps: int = 5000):
        if ip_version == 4:
            cmd = 'sudo %s -i %s -I %s -t ICMP -r %d -o %s' % (
                common.YARRP_DIR, common.YARRP_INPUT_DIR, common.INTERFACE_NAME, pps, common.YARRP_OUTPUT_DIR % (opr_id, host))
        else:
            cmd = 'sudo %s -i %s -I %s -t ICMP6 -r %d -o %s' % (
                common.YARRP_DIR, common.YARRP_INPUT_DIR, common.INTERFACE_NAME, pps, common.YARRP_OUTPUT_DIR % (opr_id, host))
        try:
            os.system(cmd)
        except Exception as e:
            common.get_logger().error("Failure in Calling Yarrp: %s", e)

    def parse_yarrp_output(self, opr_id: int, host: str) -> tuple:
        topology_dict = dict()
        node_dict = dict()  # store RTTL
        edge_dict = dict()  # (src, dst) -> real (1 or 0)
        target_dict = dict()  # node / (src, dst) -> target

        with open(common.YARRP_OUTPUT_DIR % (opr_id, host), 'r') as f:
            line = f.readline()
            for _, line in enumerate(f):
                if line[0] != '#':
                    lst = line.split()
                    target = lst[0]
                    hop = lst[6]
                    ttl = int(lst[5])
                    rttl = int(lst[11])

                    # TODO: is it possible to have multiple different RTTL's?
                    node_dict[hop] = rttl

                    target_dict[hop] = target

                    if hop != target:
                        if target not in topology_dict.keys():
                            topology_dict[target] = dict()
                        topology_dict[target][ttl] = hop

        for (target, v) in topology_dict.items():
            a = []
            for (ttl, hop) in v.items():
                a.append([ttl, hop])

            # add last hop (which is a virtual edge due to violations against inbound response)
            a.append([10000, target])

            a_sorted = sorted(a, key=lambda x: x[0])
            for i in range(len(a_sorted) - 1):
                src_ttl, src = a_sorted[i]
                dst_ttl, dst = a_sorted[i + 1]

                if src_ttl + 1 == dst_ttl:
                    edge_dict[(src, dst)] = 1
                else:
                    edge_dict[(src, dst)] = 0

                target_dict[(src, dst)] = target

        nodes = []
        for node, rttl in node_dict.items():
            if node not in self.nodes_library:
                self.nodes_library.add(node)
                nodes.append({'addr': node, 'rttl': rttl,
                              'target': target_dict[node]})

        edges = []
        for (src, dst), real in edge_dict.items():
            if ((src, dst, real) in self.edges_library) or (real == 0 and (src, dst, 1) in self.edges_library):
                continue
            edges.append({'src': src, 'dst': dst, 'real': real,
                          'target': target_dict[(src, dst)]})

            if real == 1 and (src, dst, 0) in self.edges_library:
                self.edges_library.remove(((src, dst, 0)))

            self.edges_library.add((src, dst, real))

        return nodes, edges


if __name__ == '__main__':
    topo = TopoClient()
    topo.start()
