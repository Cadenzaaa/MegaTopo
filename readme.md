# `MegaTopo`: Distrubuted Large-Scale Active Internet Topology Discovery System

![`MegaTopo` Arch] (https://github.com/Cadenzaaa/MegaTopo/blob/master/architecture.png?raw=true "Architecture of `MegaTopo`")

A great many of probers are usually required for an Internet-scale topology discovery, which may lead to huge measurement traffic and data.

With server-client architecture, `MegaTopo` has one `topo-server` and many `topo-client`s. `topo-server` sends active topology discovery commands to `topo-client`s, and then collects and analyze measurement data from them.

`MegaTopo` also uses reinforcement learning-based methods to opitmize the scheduling of active topology discovery, which results in improvement in efficency, discovering more topology nodes and edges with fewer packets to be sent.

`MegaTopo` discovers over 43M IPv6 edges with five probers, being the most large-scale IPv6 topology discovery research to date.

Read [/topo-client/readme.md](./topo-client/readme.md) and [/topo-server/readme.md](./topo-server/readme.md) for details.

# Libraries
```
MySQL
Neo4j
GeoLite2
Redis
Apache Kafka
Matplotlib
Graphviz
PyEcharts
Yarrp
```

# References
* Robert Beverly:
Yarrp'ing the Internet: Randomized High-Speed Active Topology Discovery. Internet Measurement Conference 2016: 413-420
* Robert Beverly, Ramakrishnan Durairajan, David Plonka, Justin P. Rohrer:
In the IP of the Beholder: Strategies for Active IPv6 Topology Discovery. Internet Measurement Conference 2018: 308-321
* Matthieu Gouel, Kevin Vermeulen, Maxime Mouchet, Justin P. Rohrer, Olivier Fourmaux, Timur Friedman:
Zeph & Iris map the internet: A resilient reinforcement learning approach to distributed IP route tracing. 2-9