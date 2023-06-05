import redis
import common


class RedisConn:
    def __init__(self):
        self.conn = redis.StrictRedis(
            host=common.REDIS_SERVER, port=common.REDIS_PORT, decode_responses=True)

    def set(self, key: str, value: str):
        try:
            self.conn.set(key, value)
        except Exception as e:
            common.get_logger().error('Failed to Set Redis Key-Value: %s', e)

    def get(self, key: str) -> str:
        try:
            ret = self.conn.get(key)
            return ret
        except Exception as e:
            common.get_logger().error('Failed to Get Redis Key-Value: %s', e)

    def hset(self, key: str, field: str, value: str):
        try:
            self.conn.hset(key, field, value)
        except Exception as e:
            common.get_logger().error('Failed to Set Redis Hash Value: %s', e)

    def hget(self, key: str, field: str):
        try:
            return self.conn.hget(key, field)
        except Exception as e:
            common.get_logger().error('Failed to Get Redis Hash Value: %s', e)


if __name__ == '__main__':
    redisconn = RedisConn()
    redisconn.set('foo', 'bar')
    print(redisconn.get('foo'))
