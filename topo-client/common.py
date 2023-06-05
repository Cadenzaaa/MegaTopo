import logging
import os
import configparser

TYPE_TRACEROUTE4 = 1
TYPE_TRACEROUTE6 = 2

MSG_TYPE_TRACEROUTE4 = 'traceroute4'
MSG_TYPE_TRACEROUTE4_RESULT = 'traceroute4-result'

MSG_TYPE_TRACEROUTE6 = 'traceroute6'
MSG_TYPE_TRACEROUTE6_RESULT = 'traceroute6-result'

KAFKA_SERVER = ''
KAFKA_COMMAND_TOPIC = ''
KAFKA_RESULT_TOPIC = ''

REDIS_SERVER = ''
REDIS_PORT = -1

LOCAL_IPV4_ADDR = ''
LOCAL_IPV6_ADDR = ''


CONFIG_DIR = 'config.cfg'
# Client Side Only
# ----------------------------------------
YARRP_DIR = ''
YARRP_INPUT_DIR = os.path.abspath('./output/yarrp_input.txt')
YARRP_OUTPUT_DIR = os.path.abspath('./output/yarrp_output_%d_%s.txt')
INTERFACE_NAME = ''
# ----------------------------------------


def parse_config():
    global YARRP_DIR
    global KAFKA_SERVER
    global KAFKA_COMMAND_TOPIC
    global KAFKA_RESULT_TOPIC
    global REDIS_SERVER
    global REDIS_PORT
    global LOCAL_IPV4_ADDR
    global LOCAL_IPV6_ADDR

    variables = globals()

    try:
        config_parser = configparser.ConfigParser()
        config_parser.read(CONFIG_DIR)

        yarrp_cfg = config_parser['yarrp']
        for parameter in ('YARRP_DIR', 'INTERFACE_NAME'):
            variables[parameter] = yarrp_cfg[parameter]

        server_cfg = config_parser['server']
        for parameter in ['KAFKA_SERVER', 'KAFKA_COMMAND_TOPIC', 'KAFKA_RESULT_TOPIC', 'REDIS_SERVER']:
            variables[parameter] = server_cfg[parameter]

        for parameter in ['REDIS_PORT']:
            variables[parameter] = int(server_cfg[parameter])

        ip_cfg = config_parser['ip']
        for parameter in ('LOCAL_IPV4_ADDR', 'LOCAL_IPV6_ADDR'):
            variables[parameter] = ip_cfg[parameter]

    except Exception as e:
        get_logger().error("Failure in Parsing Config: %s", e)

logger = None

def get_logger() -> logging.Logger:
    global logger
    if logger is None:
        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
    return logger
