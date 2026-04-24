## The Traditional Internet Architecture

The Internet protocol suite separates communication into layers with different responsibilities [@kurose2025]. At the network layer, IP delivers packets between hosts based on IP addresses. At the transport layer, TCP provides a reliable connection abstraction between applications. To support this abstraction, TCP maintains state about the active exchange. This separation is central to the traditional Internet architecture, but it also explains why address changes can disrupt transport connections.

This section introduces the architectural background needed to understand this limitation. It first explains the end-to-end principle and the placement of communication state at the endpoints. It then discusses how transport connections became identified through address and port information. Finally, it considers how mobility and multihoming challenge that design.

### End-to-End Principle

The coupling between transport identity and network location follows from the distribution of communication state in the Internet architecture. Internet communication is not a sequence of isolated packet deliveries, but a continuous exchange across many packets. Transport protocols present this exchange as a persistent communication abstraction. To implement this abstraction, an endpoint must maintain its state across transmissions. This state includes sequence numbers, retransmission timers, congestion-window parameters, flow-control limits, and, in modern secure transports, cryptographic context. In TCP, this information is stored in a transmission control block that records both the progress of the byte stream and the dynamics of congestion control.

The Internet architecture deliberately avoids storing this state within the network. At the IP layer, this means that packets are forwarded without retained information about past deliveries or session-level associations. Consequently, reliability and ordering cannot depend on the network core. They must instead be implemented at the endpoints. This placement creates a division between a stateless network core and stateful endpoints.

This division follows the end-to-end principle [@saltzer1984end]. The principle argues that functions requiring application-level knowledge cannot be implemented completely within intermediate nodes, since their correctness ultimately depends on the communicating endpoints. Hence, transport functions that depend on communication context belong at the endpoints rather than in the network core. This placement avoids per-session complexity in routers and allows the network core to remain simple and scalable.

According to Clark [@10.1145/52325.52336], this arrangement can be described as fate-sharing. In this model, a communication state resides only in the host that depends on it. If that host fails, the state is lost. By contrast, failures within the network may disrupt packet delivery but do not eliminate the session state maintained at the endpoints. Therefore, the architecture avoids maintaining the per-session state in the network to preserve robustness and scalability.

This endpoint placement has an important consequence: without session state in routers, endpoints must determine how each arriving packet maps to existing transport state. However, an arriving packet carries no explicit reference to a stored connection object. Therefore, the association between packet and session must be derived from fields present in the packet itself.

### Identity Versus Location

The endpoint placement of communication state creates a further requirement: endpoints must identify the relevant state from information available in arriving packets. In the classic Internet design, this identification relies on the combination of source and destination IP addresses and source and destination port numbers. For example, TCP connection state is stored in tables indexed by this four-tuple.

This mechanism was not defined as an explicit architectural principle in early Internet documents. Instead, it follows from the practical constraints of packet processing. The only stable information available in arriving packets is the network-layer address information and the transport-layer port numbers. These fields provide a compact and efficient key for associating incoming packets with existing session state. No additional namespace or connection identifier is required.

Under stable addressing conditions, this mechanism functions effectively. Provided that the four-tuple remains constant, packets can be reliably associated with the correct session state. Thus, address information serves two roles simultaneously: it directs packets through the network and contributes to the identification of the communicating session.

Prior work on the host identity protocol (HIP) describes this dual role by observing that IP addresses in the current architecture serve as both identifiers and locators [@nikander2010host]. This arrangement was historically acceptable in an environment where IP addresses were expected to change infrequently. Therefore, the architectural model treated the host location in the network topology as stable for the lifetime of a connection.

In effect, the session identity became inseparable from the network location. Accordingly, the transport layer did not maintain a separate notion of the communicating entity. Instead, it identified the session through address and port information that also described where the host was reachable in the network.

### Mobility

Address-based session identification depends on the assumption of stable addressing. Mobility challenges this assumption directly. In contemporary networks, a host may change network attachment while the application remains active, and address translation may also alter the address information visible to the transport layer.

Mobility refers to a change in the network attachment point of a host over time. At any given moment, the host typically operates through one IP address. However, during an ongoing session, the active address may change, and the identifying tuple may no longer match the stored transport state.

This tuple mismatch explains why mobility disrupts classical transport connections. The host may continue to execute the same application, and the session state may remain present in memory as buffers, congestion-window variables, and cryptographic keys. However, from the transport-layer perspective, the address component used to identify that state has changed.

Once the address component changes, incoming packets can no longer be associated with the existing state entry. Packets arriving after the change appear to belong to a different endpoint. As a result, the previous connection state becomes unreachable through the original identifier, and the session is terminated.

The resulting failure does not arise from the loss of transport state itself. Instead, it arises from the loss of a valid identifier for accessing that state. Thus, mobility exposes a structural property of the classical design: the session identity is defined indirectly through the network location.

This property connects mobility to the broader identity-location problem. A change in the network location can disrupt session continuity even when the communicating host and the application state remain active. The next subsection considers the related case of multihoming, where multiple addresses are available simultaneously rather than changing only over time.

### Multihoming

Multihoming refers to the simultaneous availability of multiple network interfaces or IP addresses. A multihomed host may maintain several valid addresses at the same time, for example, across Wi-Fi and cellular networks. These addresses may support redundancy, load balancing, or policy-based routing.

This situation differs from mobility in the timing of address availability. Mobility concerns a change in the active address over time. By contrast, multihoming concerns the presence of multiple usable addresses at the same time. In practice, the set of available addresses may also change, so mobility and multihoming can overlap.

The identity-location coupling becomes particularly visible in multihomed scenarios. A host with multiple interfaces may shift traffic from one path to another for performance or policy reasons. In the classic design, this shift changes the tuple that identifies the connection. The transport layer then treats the new path as part of a different connection instead of an alternative path for the existing one.

As a result, path selection and session continuity remain tightly coupled. A host may have several usable addresses, but the classic transport model provides no general mechanism for moving one connection among them. Multihoming therefore exposes the same structural limitation from a different direction: the session identity remains dependent on the network location.

Together, mobility and multihoming show why the identity-location problem matters for connection continuity. Mobility demonstrates the effect of an address change over time. Multihoming demonstrates the limitation of simultaneous address availability when the transport connection remains bound to one identifying tuple.
