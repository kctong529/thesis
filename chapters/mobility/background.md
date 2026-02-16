## Background

### Communication Requires Endpoint State

To understand why transport identity became coupled to network location, it is necessary to examine how the Internet architecture distributes communication state. Communication over the Internet is not a sequence of isolated packet deliveries. Transport protocols provide a higher-level abstraction: a persistent exchange that spans many packets. To implement this abstraction, the endpoint must maintain state across transmissions. This state includes sequence numbers, retransmission timers, congestion window parameters, flow-control limits, and cryptographic context in modern secure transports. In TCP, for example, this information is stored in a transmission control block that records both the progress of the byte stream and the dynamics of congestion control.

The Internet architecture deliberately avoids storing this state inside the network. The IP layer as specified does not retain information about past deliveries. It does not know which packets belong to which session, nor does it attempt to ensure reliability or ordering. These properties are implemented at the endpoints.

This division follows the end-to-end principle [@saltzer1984end], which argues that functions requiring application-level knowledge cannot be correctly implemented solely within intermediate nodes. Reliability, ordering, and correctness ultimately depend on the communicating systems themselves. Placing such mechanisms at the endpoints avoids complexity in routers and allows the network core to remain simple and scalable.

Clark later described this arrangement as fate-sharing [@10.1145/52325.52336]. Communication state resides only in the host that depends on it. If that host fails, the state is lost. By contrast, failures within the network may disrupt packet delivery but do not eliminate the session state maintained at the endpoints. The architecture thus trades per-session state in the network for robustness and scalability.

However, this decision has an important consequence: since routers do not track sessions, endpoints must determine how each arriving packet maps to existing transport state. A packet carries no explicit reference to a stored connection object. The association between packet and session must be derived from fields present in the packet itself.

### Session Identity Derived from Network Location

Because this state is maintained at the endpoints, it must be indexed using information available in arriving packets. In the classical Internet design, this indexing is based on the combination of source and destination IP addresses together with their port numbers. TCP connection state, for example, is stored in tables keyed by this four-tuple of IP addresses and port numbers.

This mechanism is not explicitly presented in early architectural documents as a philosophical stance; rather, it emerges naturally from implementation constraints. The only stable information available to both communicating hosts and routers is the network-layer addressing and transport-layer port numbers. Using these values to identify sessions is straightforward and efficient. No additional namespace or identifier needs to be introduced.

Under stable addressing conditions, the approach works well. As long as this combination remains constant, packets can be reliably associated with the correct session state. The addressing information thus serves two roles simultaneously: it directs packets through the network and identifies the communicating endpoints.

As later observed in the Host Identity Protocol literature, "in the current IP architecture, the IP addresses assume the dual role of acting both as host identifiers and locators" [@nikander2010host]. This dual role was historically acceptable because IP addresses were expected to change infrequently. The architectural model implicitly assumed that a host's location in the network topology was stable for the lifetime of a connection.

In effect, session identity became inseparable from network location. The transport layer did not maintain a separate notion of "who" was communicating; it relied on "where" the host was located.

### When Location Changes but Identity Persists

Modern networks violate the assumption of address stability. Hosts are frequently mobile. Devices may transition between networks while maintaining active applications. Network address translation may rewrite source addresses and ports.

A host may also be multihomed, meaning that it possesses multiple network interfaces or IP addresses that can be used concurrently or alternately for communication. Multihoming may arise from physical interface diversity, such as simultaneous Wi-Fi and cellular connectivity, or from logical configurations such as virtual interfaces and address aliases. Mobility concerns changes over time, whereas multihoming concerns the simultaneous presence of multiple valid addresses.

In such environments, a host may continue executing applications while its externally visible IP address changes. From the host's perspective, the session state remains intact: buffers, congestion window variables, and cryptographic keys are still present in memory. From the transport layer's perspective, however, the identifying tuple has changed.

When the address component of the tuple changes, the transport layer cannot match incoming packets to the existing state entry. The new packets appear to originate from an unknown endpoint. The previous connection state becomes unreachable, and the session is terminated.

The failure is therefore not due to loss of transport state. It arises because the identifier used to index that state is no longer valid. Mobility exposes a structural property of the classical design: identity is defined indirectly through location.

This fragility becomes particularly visible in multihomed scenarios. A host with multiple interfaces may wish to shift traffic from one path to another due to performance or policy reasons. In the classical design, however, such a shift changes the tuple that defines the connection itself. Path selection and session continuity are therefore tightly coupled, even though they conceptually address different concerns.
