> The alternative, which this architecture chose, is to take this information and gather it at the endpoint of the net, at the entity which is utilizing the service of the network.

> I call this approach to reliability 'fate-sharing.' The fate-sharing model suggests that it is acceptable to lose the state information associated with an entity if, at the same time, the entity itself is lost.

- Transport-layer state lives at endpoints
- The network core is not supposed to hold session state

> The intermediate packet switching nodes, or gateways, must not have any essential state information about on-going connections. Instead, they are stateless packet switches, a class of network design sometimes called a 'datagram' network.

- IP provides routing, not session identity
- The core network does not track connections
- Transport must handle identity/state

> If two entities are communicating over the Internet... the entities communicating should be able to continue without having to reestablish or reset the high level state of their conversation.

> At the top of transport, there is only one failure, and it is total partition.

- Transport state survives network reconfiguration
- Identity continuity is preserved despite path failure

> The Internet architecture achieves this flexibility by making a minimum set of assumptions about the function which the net will provide.

> The basic assumption is that network can transport a packet or datagram.

- IP provides delivery of packets
- It does not define identity semantics

> The datagram provides a basic building block out of which a variety of types of service can be implemented.

> It is important to understand that the role of the datagram in this respect is as a building block, and not as a service in itself.

- IP is not a session abstraction
- Transport builds session semantics on top

> This suggests that there may be a better building block than the datagram... it would identify a sequence of packets traveling from the source to the destination... I have used the word 'flow' to characterize this building block.

Clark (1988) suggests:

- A building block identifying a sequence of packets
- Without assuming service semantics
- Possibly requiring gateway flow state

This concept is conceptually similar to:

- QUIC Connection ID
- Flow identification independent of transport semantics
