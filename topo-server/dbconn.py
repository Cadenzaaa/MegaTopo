import pymysql
import common
import geoip2.database
import time


class DBConn:
    def __init__(self):
        self.conn = self.get_db_conn()
        self.cursor = self.conn.cursor()
        self.georeader = geoip2.database.Reader(common.GEODB_DIR)

    def get_db_conn(self):
        conn = pymysql.connect(host=common.MYSQL_HOST, user=common.MYSQL_USER,
                               password=common.MYSQL_PASSWORD, database='Topo')
        return conn

    def insert_nodes(self, nodes: list, opr_id: int, ip_version: int = 4):
        common.get_logger().debug('Saving Traceroute Results of Nodes (%d Nodes) in Database...' %
                                  len(nodes))
        SQL = """
        INSERT IGNORE INTO Node (node_addr, opr_id, node_ipver)
        VALUES (%s, %s, %s)
        """

        params = []
        for node in nodes:
            params.append((node['addr'], opr_id, ip_version))

        max_tries = 5
        while True:
            ok = True
            max_tries -= 1
            try:
                self.cursor.executemany(SQL, params)
                self.conn.commit()
            except Exception as e:
                common.get_logger().error("Failed to Insert Nodes: %s, %d times to retry" %
                                          (e, max_tries))
                self.conn.rollback()
                ok = False
            finally:
                if ok or max_tries <= 0:
                    break
                time.sleep(5)

        common.get_logger().debug('Traceroute Results of Nodes Saved in Database')

    def insert_rttl(self, nodes: list, host: str, opr_id: int):
        common.get_logger().debug('Saving Traceroute Results of Node RTTLs (%d Nodes) in Database...' %
                                  len(nodes))
        SQL = """
        INSERT IGNORE INTO RTTL (node_addr, host_addr, opr_id, rttl)
        VALUES (%s, %s, %s, %s)
        """
        params = []
        for node in nodes:
            params.append((node['addr'], host, opr_id, node['rttl']))

        max_tries = 5
        while True:
            ok = True
            max_tries -= 1
            try:
                self.cursor.executemany(SQL, params)
                self.conn.commit()
            except Exception as e:
                common.get_logger().error("Failed to Insert RTTL's: %s, %d time(s) to retry" %
                                          (e, max_tries))
                self.conn.rollback()
                ok = False
            finally:
                if ok or max_tries <= 0:
                    break
                time.sleep(5)

        common.get_logger().debug('Traceroute Results of Node RTTLs Saved in Database')

    # def insert_edges(self, edges: set, opr_id: int):
    #     SQL = """
    #     INSERT INTO Route
    #     SET addr1 = %s, addr2 = %s, opr_id = %s
    #     """
    #     params = []
    #     for edge in edges:
    #         params.append((edge[0], edge[1], opr_id))
    #     try:
    #         self.cursor.executemany(SQL, params)
    #         self.conn.commit()
    #     except Exception as e:
    #         common.get_logger().error("Failed to Insert New Edges:", e)
    #         self.conn.rollback()

    def insert_geo(self, nodes: set, opr_id: int):
        n = len(nodes)
        params = []
        err = 0
        geo = dict()
        for node in nodes:
            try:
                ret = self.georeader.city(node)
                lng, lat = ret.location.longitude, ret.location.latitude
                params.append((node, opr_id, lng, lat))
                geo[node] = (lng, lat)
            except:
                err += 1

        if err > 0:
            common.get_logger().info(
                "Geolocation : Success Rate %d / %d" % (n - err, n))

        SQL = """
        INSERT INTO Geolocation
        SET node_addr = %s, opr_id = %s, node_lng = %s, node_lat = %s
        """
        try:
            self.cursor.executemany(SQL, params)
            self.conn.commit()
        except Exception as e:
            common.get_logger().error(
                "Failed to Insert New Geolocation Information:", e)
            self.conn.rollback()

        return geo

    def init_opereation(self, opr_type: int, opr_desc: str) -> int:
        # now = datetime.datetime.now()
        # now = now.strftime("%Y-%m-%d %H:%M:%S")
        SQL = """
        INSERT INTO Operation
        SET opr_type = %s, descr = %s
        """
        max_tries = 5
        while True:
            ok = True
            max_tries -= 1
            try:
                self.cursor.execute(SQL, [opr_type, opr_desc])
                self.conn.commit()
            except Exception as e:
                common.get_logger().error(
                    "Failed to Initiate New Operation: %s, %d time(s) to retry" % (e, max_tries))
                self.conn.rollback()
                ok = False
            finally:
                if ok or max_tries <= 0:
                    break
                time.sleep(5)
        return self.get_last_id()

    def get_last_id(self) -> int:
        SQL = """
        SELECT LAST_INSERT_ID()
        """
        max_tries = 5
        while True:
            ok = True
            max_tries -= 1
            try:
                self.cursor.execute(SQL)
            except Exception as e:
                common.get_logger().error("Failed to Get Last ID: %s, %d time(s) to retry" %
                                          (e, max_tries))
                ok = False
            finally:
                if ok or max_tries <= 0:
                    break
                time.sleep(5)

        results = self.cursor.fetchall()
        if len(results) == 0 or len(results[0]) == 0:
            common.get_logger().error("Last ID Not Found: %s" % e)
        return results[0][0]
