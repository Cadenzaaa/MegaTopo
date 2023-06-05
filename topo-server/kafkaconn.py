from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import common


class KafkaConn:
    def __init__(self):
        self.cmd_consumer = KafkaConsumer(common.KAFKA_COMMAND_TOPIC,
                                          bootstrap_servers=[common.KAFKA_SERVER])
        self.cmd_producer = KafkaProducer(bootstrap_servers=[
            common.KAFKA_SERVER], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.res_consumer = KafkaConsumer(common.KAFKA_RESULT_TOPIC,
                                          bootstrap_servers=[common.KAFKA_SERVER])
        self.res_producer = KafkaProducer(bootstrap_servers=[
            common.KAFKA_SERVER], value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def cmd(self, res: dict):
        try:
            self.res_producer.send(common.KAFKA_COMMAND_TOPIC, res)
            self.res_producer.flush()
        except Exception as e:
            common.get_logger().error('Failed to Send Command Messages to Kafka: %s', e)

    def res(self, res: dict):
        try:
            self.res_producer.send(common.KAFKA_RESULT_TOPIC, res)
            self.res_producer.flush()
        except Exception as e:
            common.get_logger().error('Failed to Send Result Messages to Kafka: %s', e)


if __name__ == '__main__':
    kafkaconn = KafkaConn()
    kafkaconn.start()
