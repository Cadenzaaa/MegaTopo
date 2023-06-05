import pygraphviz
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType
from dbconn import DBConn
from kafkaconn import KafkaConn
from redisconn import RedisConn
from neo4jconn import Neo4jConn
import time
import common
import json
import threading
from collections import defaultdict


class TopoServer:
    def __init__(self):
        common.parse_config()

        self.kafkaconn = KafkaConn()
        self.dbconn = DBConn()
        self.redisconn = RedisConn()
        self.neo4jconn = Neo4jConn()

        self.kafkathread = threading.Thread(target=self.run, daemon=True)
        self.pointthread = threading.Thread(
            target=self.record_points, daemon=True)
        self.point_lock = threading.Lock()

        self.nodes_library = set()
        self.edges_library = set()

        self.points = defaultdict(int)
        
        # How many points the target get if one new node/edge was discovered by sending probes to this target.
        self.POINTS_PER_NODE = 5
        self.POINTS_PER_EDGE = 1

        self.met = set()

    def run(self):
        cnt = 0
        for msg in self.kafkaconn.res_consumer:
            self.process(msg.value)
            cnt += 1
            if cnt % 100 == 0:
                common.get_logger().info('%d Messages Handled' % cnt)

    # Record the points of targets periodically.
    def record_points(self):
        while True:
            self.point_lock.acquire()
            if len(self.points) != 0:
                common.get_logger().debug('Recording Points...')
                points_sorted = sorted(
                    self.points.items(), key=lambda x: x[1], reverse=True)
                with open(common.POINTS_FILE, 'w') as f:
                    for addr, point in points_sorted:
                        print(addr, point, file=f)

                common.get_logger().debug('Finished Recording Points')
            self.point_lock.release()
            time.sleep(180)

    def start(self):
        common.get_logger().info('Start Running')
        self.kafkathread.start()
        self.pointthread.start()

    def stop(self):
        common.get_logger().info('Stop Running')

    def process(self, msg: bytes):
        msg_dict = json.loads(msg)
        common.get_logger().debug('Results Received: %s', msg_dict.__str__()
                                  [:1000])  # Show 1k characters at most
        if msg_dict['type'] == common.MSG_TYPE_TRACEROUTE4_RESULT:
            self.parse_traceroute_result(msg_dict, 4)
        elif msg_dict['type'] == common.MSG_TYPE_TRACEROUTE6_RESULT:
            self.parse_traceroute_result(msg_dict, 6)

    def parse_traceroute_result(self, msg_dict: dict, ip_version: int = 4):
        opr_id = int(msg_dict['opr_id'])
        host = msg_dict['host']
        nodes_rcvd = msg_dict.get('nodes', [])
        edges_rcvd = msg_dict.get('edges', [])
        finished = msg_dict.get('finished', 0)

        if opr_id not in self.met:
            self.met.add(opr_id)
            common.get_logger().info('Starting Operation ID: %d, Points Cleared' % opr_id)
            self.point_lock.acquire()
            # self.points.clear()
            for k in self.points:
                self.points[k] = round(self.points[k] * 0.7)
            self.point_lock.release()

        key = '%d-%s' % (opr_id, host)
        if key not in self.met:
            self.met.add(key)
            common.get_logger().info('New Results Received: %s', msg_dict.__str__()
                                     [:1000])  # Show 1k characters at most

        nodes = []
        edges = []
        self.point_lock.acquire()

        for node in nodes_rcvd:
            if node['addr'] not in self.nodes_library:
                self.nodes_library.add(node['addr'])
                nodes.append(node)
                self.points[node['target']] += self.POINTS_PER_NODE

        for edge in edges_rcvd:
            src, dst, real, target = edge['src'], edge['dst'], edge['real'], edge['target']
            if ((src, dst, real) in self.edges_library) or (real == 0 and (src, dst, 1) in self.edges_library):
                continue

            if real == 1 and (src, dst, 0) in self.edges_library:
                self.edges_library.remove(((src, dst, 0)))

            self.edges_library.add((src, dst, real))
            edges.append(edge)
            self.points[target] += self.POINTS_PER_EDGE

        self.point_lock.release()

        if len(nodes) > 0:
            self.dbconn.insert_nodes(
                nodes, opr_id, ip_version)
            self.dbconn.insert_rttl(nodes, host, opr_id)

        if len(edges) > 0:
            self.neo4jconn.insert_edges(
                edges, opr_id, ip_version)

        if finished == 1:
            if len(nodes) > 0:
                common.get_logger().info('Nodes Finished: opr_id=%d, host=%s' % (opr_id, host))
            if len(edges) > 0:
                common.get_logger().info('Edges Finished: opr_id=%d, host=%s' % (opr_id, host))
                self.redisconn.hset(str(opr_id) + ':status', host, 'C')


    # Draw topology with pygraphviz
    def draw_topology(self, edges: set, output_dir: str):
        graph = pygraphviz.AGraph(directed=True)
        graph.node_attr['style'] = 'filled'
        for edge in edges:
            graph.add_edge(edge[0], edge[1])
        graph.layout('dot')
        graph.draw(output_dir + '.pdf')

    # Draw topology with pyecharts. Geolocation is required.
    def draw_topology_with_geolocation(self, edges: set, geo: dict, output_dir: str):
        g = Geo().add_schema(maptype="world")
        for addr, pos in geo.items():
            g.add_coordinate(addr, pos[0], pos[1])
        g.add(
            "",
            list(edges),
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW, symbol_size=6, color="blue"
            ),
            linestyle_opts=opts.LineStyleOpts(curve=0.2),
        )
        g.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        # g.set_global_opts(title_opts=opts.TitleOpts(title="Geo-Lines"))
        g.render(output_dir + '.html', width='1920px', height='1080px')


if __name__ == '__main__':
    server = TopoServer()
    server.start()

    while True:
        try:
            pass
        except KeyboardInterrupt as e:
            server.stop()
            break
