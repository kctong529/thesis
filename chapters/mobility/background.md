## The Traditional Internet Architecture

The Internet protocol suite separates communication into layers with different responsibilities [@kurose2025]. At the network layer, IP delivers packets between hosts based on IP addresses. At the transport layer, TCP provides a reliable connection abstraction between applications. To support this abstraction, TCP maintains state about the active exchange. This separation is central to the traditional Internet architecture, but it also explains why address changes can disrupt transport connections.

This section introduces the architectural background needed to understand this limitation. It first explains the end-to-end principle and the placement of communication state at the endpoints. It then discusses how transport connections became identified through address and port information. Finally, it considers how mobility and multihoming challenge that design.

### End-to-End Principle

The coupling between session identity and network location follows from the distribution of communication state in the Internet architecture. Internet communication is not a sequence of isolated packet deliveries, but a continuous exchange across many packets. This exchange is presented in transport protocols as a persistent communication abstraction. To implement this abstraction, an endpoint must maintain its state across transmissions. This state contains information such as sequence numbers, retransmission timers, congestion-window parameters, flow-control limits, and cryptographic context.

The Internet architecture deliberately avoids storing this state within the network infrastructure. At the IP layer, this means that packets are forwarded without retained information about past deliveries or session-level associations. Reliability and ordering cannot depend on the network core and must be implemented at the endpoints. This placement creates a division between a stateless network core and stateful endpoints.

This division follows the end-to-end principle [@saltzer1984end]. The principle argues that functions which require application-level knowledge depend on the communicating endpoints to guarantee correctness. Hence, they cannot be implemented completely within intermediate nodes. This implies that transport functions which depend on communication context should belong at the endpoints but not in the network core.

According to Clark [@10.1145/52325.52336], this arrangement can be described as fate-sharing. In this placement model, communication state resides only in the host that depends on it. If that host fails, the state is lost. By contrast, failures within the network may disrupt packet delivery but do not eliminate the session state maintained at the endpoints. Therefore, the architecture avoids maintaining the per-session state in the network to preserve robustness and scalability.

This endpoint placement has an important consequence: without session state in routers, endpoints must determine how each arriving packet maps to existing transport state. However, an arriving packet carries no explicit reference to a stored connection object. The endpoint must derive the association between the packet and session from fields present in the packet itself.

### Identity Versus Location

The endpoint placement of communication state creates a further requirement: endpoints must identify the relevant state from information available in arriving packets. In the classic Internet design, this identification relies on the source and destination IP addresses and port numbers. For example, TCP connection state is stored in tables indexed by this four-tuple.

This mechanism was not defined as an explicit architectural principle in early Internet documents. Instead, it follows from the practical constraints of packet processing. Without a separate session identifier, endpoints used the network-layer addresses and transport-layer port numbers carried in each packet as a compact and efficient key that associated each packet with the relevant session state.

Thus, address information traditionally serves two roles at the same time. It directs packets through the network and contributes to the identification of the transport connection. Prior work on the host identity protocol (HIP) describes this dual role by noting that IP addresses in the current architecture serve as both identifiers and locators [@nikander2010host].

This dual role creates a limitation for TCP: packets can be associated with the existing connection state only while the four-tuple remains constant. This limitation was less apparent in the environments for which the architecture was originally developed, since IP addresses were generally expected to remain stable for the lifetime of a connection. In effect, the architectural model treated the network locations of the communicating hosts as fixed during an ongoing exchange.

Consequently, session identity became coupled to network location. The transport layer did not maintain a separate identifier for the ongoing communication or the communicating endpoint. Instead, it identified the session through address and port information that also indicated where the host was reachable in the network.

### Mobility

Mobility refers to a change in the network attachment point of a host while communication remains active [@kurose2025]. For example, a host may move from a Wi-Fi network to a cellular network and receive a new IP address even though the application and transport state remain unchanged. Such a change challenges address-based session identification, which assumes that the relevant addresses remain stable.

Suppose that a TCP endpoint changes from one interface to another and receives a new IP address. The source address in its packets then changes, while the port numbers, application state, and transport state may remain unchanged. The peer receives packets whose four-tuple no longer matches the entry associated with the original connection.

The address change does not necessarily erase the transport state. The endpoint may still retain buffers, sequence numbers, congestion-control variables, retransmission timers, and cryptographic context until the connection closes or expires. However, the transport protocol lacks an address-independent session identifier through which it could associate packets from the new path with that state.

As a result, the original state remains bound to the old tuple. Packets that use the new address appear to belong to another communication context, and the endpoint cannot treat them as a continuation of the existing session. Unless another mechanism preserves the association, communication must continue over the old path or through a new transport connection.

More broadly, mobility exposes the identity-location coupling. A host and its application state may remain unchanged, yet a change in network attachment can interrupt session continuity because the address forms part of the session identifier. The next subsection considers multihoming, in which a host has several valid addresses at the same time rather than one address after another.

### Multihoming

Multihoming refers to a configuration in which a host has more than one network connection or IP address at the same time [@kurose2025]. For example, a host may have active Wi-Fi and cellular interfaces, each with a separate IP address. The term may also describe a network connected to multiple Internet service providers, but this thesis focuses on host multihoming and its effect on transport sessions.

This situation differs from mobility in the timing of address availability. Mobility concerns a change in the active address over time. By contrast, multihoming concerns the presence of multiple usable addresses at the same time. In practice, the set of available addresses may also change, so mobility and multihoming can overlap.

The identity-location coupling becomes particularly visible in multihomed scenarios. A host with multiple interfaces may shift traffic from one path to another for performance or policy reasons. In the classic design, this shift changes the tuple that identifies the connection. The transport layer then treats the new path as part of a different connection instead of an alternative path for the existing one.

As a result, path selection and session continuity remain tightly coupled. A host may have several usable addresses, but the classic transport model provides no general mechanism for moving one connection among them. Therefore, multihoming exposes the same limitation from a different direction: the transport layer does not automatically associate alternative addresses with the existing session.

Both cases expose the identity-location coupling. An address change disrupts continuity under mobility, while the presence of several valid addresses does not by itself allow a session to move between paths. In either case, the identifying tuple prevents the transport state from moving transparently to another network path.
