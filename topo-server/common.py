import logging
import configparser

TYPE_TRACEROUTE4 = 1
TYPE_TRACEROUTE6 = 2

MSG_TYPE_TRACEROUTE4 = 'traceroute4'
MSG_TYPE_TRACEROUTE4_RESULT = 'traceroute4-result'

MSG_TYPE_TRACEROUTE6 = 'traceroute6'
MSG_TYPE_TRACEROUTE6_RESULT = 'traceroute6-result'

KAFKA_SERVER = 'localhost:9092'
KAFKA_COMMAND_TOPIC = 'topo-command-topic'
KAFKA_RESULT_TOPIC = 'topo-result-topic'

REDIS_SERVER = 'localhost'
REDIS_PORT = 6379

CONFIG_DIR = 'config.cfg'

# Server-side Only
# ----------------------------------------
GEODB_DIR = './data/GeoLite2-City.mmdb'

NEO4J_URL = ''
NEO4J_USERNAME = ''
NEO4J_PASSWORD = ''

PROBERS = []

MYSQL_HOST = ''
MYSQL_USER = ''
MYSQL_PASSWORD = ''

POINTS_FILE = 'points.txt'
# ----------------------------------------

def parse_config():
    global NEO4J_URL
    global NEO4J_USERNAME
    global NEO4J_PASSWORD
    
    global PROBERS
    
    global MYSQL_HOST 
    global MYSQL_USER 
    global MYSQL_PASSWORD

    variables = globals()

    try:
        config_parser = configparser.ConfigParser()
        config_parser.read(CONFIG_DIR)

        neo4j_cfg = config_parser['neo4j']
        for parameter in ('NEO4J_URL', 'NEO4J_USERNAME', 'NEO4J_PASSWORD'):
            variables[parameter] = neo4j_cfg[parameter]
            
        prober_cfg = config_parser['prober']
        for parameter in ['PROBERS']:
            variables[parameter] = prober_cfg[parameter].split(',')
            
        mysql_cfg = config_parser['mysql']
        for parameter in ('MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD'):
            variables[parameter] = mysql_cfg[parameter]
        
    except Exception as e:
        get_logger().error("Failure in Parsing Config: %s", e)
        
logger = None

def get_logger()->logging.Logger:
    global logger
    if logger is None:
        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
    return logger