> "It allows connections to migrate across IP address changes by using a Connection ID to identify connections instead of the IP/port 5-tuple."

- Explicit decoupling of transport connection identity from network-layer addressing
- Architectural shift from implicit (5-tuple) to explicit identity

> "QUIC connections are identified by a 64-bit Connection ID. QUIC's Connection ID enables connections to survive changes to the client's IP and port."

> "Such changes can be caused by NAT timeout and rebinding ... or by the client changing network connectivity to a new IP address."

- NAT rebinding
- Modern networks have frequent address and port changes due to mobility and NAT behavior
- Real-world motivation

> "The Connection ID serves routing and identification purposes; it is used by load balancers to direct the connection's traffic to the right server and by the server to locate connection state."

- Connection ID indexes connection state
- It is visible in the header
- It replaces the 5-tuple as the primary key for locating transport state
- Support definition of session: identity encoded explicitly in packet header

> "Deploying changes to all three components requires incentivizing and coordinating between application developers, OS vendors, middlebox vendors, and the network operators that deploy these middleboxes."

> "QUIC encrypts transport headers and builds transport functions atop UDP, avoiding dependence on vendors and network operators and moving control of transport deployment to the applications that directly benefit from them."

- Ossification and deployment constraints
- Architectural coupling: TCP identity tied to 5-tuple
- Ecosystem coupling: Middleboxes depend on TCP semantics
- Institutional coupling: Kernel implementation slows evolution
- TCP evolution requires ecosystem-wide coordination, which makes deployment of new mechanisms significantly slow
- Socio-technical rigidity due to accumulated dependencies across software, hardware, and operational practices
- QUIC uses Connection ID
- QUIC avoid most transport metadata, which reduces reliance on transport internals by middleboxes
- The transport logic is no longer inside the OS kernel
- QUIC implements transport functions in user space over UDP, and reduces dependence on kernel upgrades for transport evolution

> "QUIC's design is closest to that of Structured Stream Transport (SST)... SST uses a channel identifier... encrypts the transport header, and employs lightweight streams."

- Evolution of transport abstraction
- There were conceptual precursors to QUIC's abstraction shift
- QUIC builds on earlier ideas of stream multiplexing and encrypted transport headers
