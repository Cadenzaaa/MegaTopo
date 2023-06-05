from kafkaconn import KafkaConn
from redisconn import RedisConn
from dbconn import DBConn
import common
import random
import time


class TopoShell:
    def __init__(self):
        self.kafkaconn = KafkaConn()
        self.redisconn = RedisConn()
        self.dbconn = DBConn()
        self.probers = common.PROBERS

    def traceroute(self, probers: list, targets: list, ip_version: int = 4) -> int:
        cmd = {
            'type': 'traceroute' + str(ip_version),
            'host': probers,
        }
        common.get_logger().info('Starting New Traceroute Operation: %s', cmd)
        try:
            opr_id = self.dbconn.init_opereation(
                common.TYPE_TRACEROUTE4 if ip_version == 4 else common.TYPE_TRACEROUTE6, str(cmd))
            common.get_logger().info('Operation ID: %d' % opr_id)

            cmd['opr_id'] = opr_id
            self.kafkaconn.cmd(cmd)

            common.get_logger().info('Command Sent to the Message Queue')
            self.redisconn.set(str(opr_id) + ':target', '\n'.join(targets))
            common.get_logger().info('Target Redis Set')
            for prober in probers:
                self.redisconn.hset(str(opr_id) + ':status', prober, 'S')
            common.get_logger().info('Status Redis Set')
            return opr_id
        except Exception as e:
            common.get_logger().error(e)
            return -1

    # Brute-force measurements. Every prober sends probes to every target.
    def bftraceroute(self, zlen: int):
        targets = []

        with open('data/z%d.txt' % zlen, 'r') as f:
            for _, line in enumerate(f):
                targets.append(line.strip())
        random.shuffle(targets)

        self.traceroute(self.probers, targets, ip_version=6)

    # Opitmized RL-based measurements.
    # High-value targets (with which more edges and nodes discovered) will be repeatedly probed.
    def rltraceroute(self, zlen: int):
        targets = []

        with open('data/z%d.txt' % zlen, 'r') as f:
            for _, line in enumerate(f):
                targets.append(line.strip())
        random.shuffle(targets)

        rounds = 9 + 50
        eps = 0.5
        common.get_logger().info('%d Rounds, Eps = %f' % (rounds, eps))

        # n_parts = rounds + 1
        n_parts = 10
        len_per_part = len(targets) // n_parts
        common.get_logger().info('%d Targets, %d Targets Per Part' %
                                 (len(targets), len_per_part))

        parts = []
        for i in range(n_parts):
            if i < n_parts - 1:
                parts.append(targets[i * len_per_part: (i + 1) * len_per_part])
            else:
                parts.append(targets[i * len_per_part:])

        exploitation = []
        for r in range(rounds):
            common.get_logger().info('Round #%d Begins' % (r + 1))
            opr = []
            if r == 0:
                curr = 0
                for prober in self.probers:
                    p1 = curr

                    curr += 1
                    if curr >= n_parts:
                        curr = curr % n_parts

                    p2 = curr

                    common.get_logger().info('Part #%d, #%d for Prober #%d: %s' %
                                             (p1, p2, self.probers.index(prober), prober))
                    opr_id = self.traceroute(
                        [prober], parts[p1] + parts[p2], ip_version=6)
                    opr.append((opr_id, prober))

                    curr += 1
                    if curr >= n_parts:
                        curr = curr % n_parts

            else:
                curr = 2 + (r - 1)
                if curr >= n_parts:
                    curr = curr % n_parts
                for prober in self.probers:
                    common.get_logger().info('Part #%d for Prober #%d: %s' %
                                             (curr, self.probers.index(prober), prober))
                    opr_id = self.traceroute(
                        [prober], parts[curr] + exploitation, ip_version=6)
                    opr.append((opr_id, prober))

                    curr += 2
                    if curr >= n_parts:
                        curr = curr % n_parts

            while True:
                ok = True
                for opr_id, prober in opr:
                    status = self.redisconn.hget('%d:status' % opr_id, prober)
                    if not status or status != 'C':
                        ok = False
                        break
                if ok:
                    break
                time.sleep(300)

            time.sleep(180)
            time.sleep(600)

            # Exploitation, repeatedly send probes to high-value targets
            exploitation = []
            s = set()
            exploitation_len = round(len_per_part / eps * (1 - eps))
            with open(common.POINTS_FILE, 'r') as f, open('points_round_%d.txt' % (r + 1), 'w') as g:
                for _, line in enumerate(f):
                    if len(s) < exploitation_len:
                        s.add(line.split()[0])
                        g.write(line)
                    else:
                        break
            exploitation = list(s)


if __name__ == '__main__':
    shell = TopoShell()
    # shell.bftraceroute(64)
    shell.rltraceroute(64)
