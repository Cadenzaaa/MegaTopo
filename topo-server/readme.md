# Install Python Packages
`pip3 install -r requirements.txt`

# Kafka
## Start Kafka Service

```
bin/zookeeper-server-start.sh -daemon config/zookeeper.properties
bin/kafka-server-start.sh -daemon config/server.properties
```

## Create Topics

```
bin/kafka-topics.sh --create --partitions 1 --replication-factor 1 --topic topo-command-topic --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --partitions 1 --replication-factor 1 --topic topo-result-topic --bootstrap-server localhost:9092

```

## Test Kafka Topics
### Describe Topics
```
bin/kafka-topics.sh --describe --topic <topic-name> --bootstrap-server [2001:1234::1]:9092
```
### Show Command Messages
```
bin/kafka-console-consumer.sh --topic topo-command-topic  --from-beginning --bootstrap-server [2001:1234::1]:9092
```

### Send Messages
```
bin/kafka-console-producer.sh --topic <topic name> --bootstrap-server [2001:1234::1]:9092
```

## Kafka Messages

### traceroute
```
{
    "type": "traceroute",
    "opr_id": 4455,
    "host": ["1.1.1.1", "2.2.2.2"],
}
```

### traceroute result
```
traceroute-result
{
    "type": "traceroute-result",
    "host": "123.123.123.123",
    "opr_id": 4455,
    "edges":
    [
        {"src":"1.1.1.1", "dst":"2.2.2.2", "real":1, "target":"8.8.8.8"}，
        {"src":"2.2.2.2", "dst":"3.3.3.3", "real":1, "target":"8.8.8.8"}，
        {"src":"3.3.3.3", "dst":"4.4.4.4", "real":0, "target":"9.9.9.9"}
    ],
    "nodes":
    [
        {"addr":"1.1.1.1", "rttl":60, "target": "8.8.8.8"},
        {"addr":"2.2.2.2", "rttl":52, "target": "9.9.9.9}
    ],
    <"finished": 1> (optional)
}
```

# Redis
Data Format:
```
key:
    <opr_id>:target
value:
    "<target1>\n<target2>\n..."
```

```
key:
    <opr_id>:status
value:
    key: 
        <host1>
    value:
        "S" | "P" | "F" | "C" (Submitted, Processing, Finished, Completed)
    key: 
        <host2>
    value:
        "S" | "P" | "F" | "C"
    key: 
        <host3>
    value:
        "S" | "P" | "F" | "C"
    ...
```

# MySQL
Create Tables:
```
source createTable.sql
```

# Neo4j
Add Neo4j Restraints:
```
CREATE CONSTRAINT ON (node: IPv4Node) assert node.name is unique
CREATE CONSTRAINT ON (node: IPv6Node) assert node.name is unique
```


# Clean-Up
```
MATCH (n) DETACH DELETE n;
FLUSHDB
source clean.sql
```

# Usage (Specify your measurement method and targets by modifying `topo-shell.py`)
```
python3 topo-server.py
python3 topo-shell.py 
```