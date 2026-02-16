
## Communication Requires Endpoint State

Communication over the Internet is not a sequence of isolated packet deliveries. Transport protocols provide a higher-level abstraction: a persistent exchange that spans many packets. To implement this abstraction, the endpoint must maintain state across transmissions. This state includes sequence numbers, retransmission timers, congestion window parameters, flow-control limits, and cryptographic context in modern secure transports. In TCP, for example, this information is stored in a transmission control block that records both the progress of the byte stream and the dynamics of congestion control.

The Internet architecture deliberately avoids storing this state inside the network. The IP layer forwards packets independently and does not retain information about past deliveries. It does not know which packets belong to which session, nor does it attempt to ensure reliability or ordering. These properties are implemented at the endpoints.

This division follows the end-to-end principle [@saltzer1984end], which argues that functions requiring application-level knowledge cannot be correctly implemented solely within intermediate nodes. Reliability, ordering, and correctness ultimately depend on the communicating systems themselves. Placing such mechanisms at the endpoints avoids complexity in routers and allows the network core to remain simple and scalable.

Clark later described this arrangement as fate-sharing [@10.1145/52325.52336]. Communication state resides only in the host that depends on it. If that host fails, the state is lost. By contrast, failures within the network may disrupt packet delivery but do not eliminate the session state maintained at the endpoints. The architecture thus trades per-session state in the network for robustness and scalability.

However, this decision has an important consequence: since routers do not track sessions, endpoints must determine how each arriving packet maps to existing transport state. A packet carries no explicit reference to a stored connection object. The association between packet and session must be derived from fields present in the packet itself.

## Session Identity Derived from Network Location

Because transport state is maintained at the endpoints, a host must index that state using information available in each packet. In the classical Internet design, this indexing is based on the combination of source and destination IP addresses together with their port numbers. TCP connection state, for example, is stored in tables keyed by this four-tuple.

This mechanism is not explicitly presented in early architectural documents as a philosophical stance; rather, it emerges naturally from implementation constraints. The only stable information available to both communicating hosts and routers is the network-layer addressing and transport-layer port numbers. Using these values to identify sessions is straightforward and efficient. No additional namespace or identifier needs to be introduced.

Under stable addressing conditions, the approach works well. As long as the tuple remains constant, packets can be reliably associated with the correct session state. The addressing information thus serves two roles simultaneously: it directs packets through the network and identifies the communicating endpoints.

As later observed in the Host Identity Protocol literature, "in the current IP architecture, the IP addresses assume the dual role of acting both as host identifiers and locators" [@nikander2010host]. This dual role was historically acceptable because IP addresses were expected to change infrequently. The architectural model implicitly assumed that a host's location in the network topology was stable for the lifetime of a connection.

In effect, session identity became inseparable from network location. The transport layer did not maintain a separate notion of "who" was communicating; it relied on "where" the host was located.

## When Location Changes but Identity Persists

Modern networks violate the assumption of address stability. Hosts are frequently mobile. Devices may transition between networks while maintaining active applications. Network address translation may rewrite source addresses and ports. Multihomed hosts may use multiple interfaces simultaneously.

In such environments, a host may continue executing applications while its externally visible IP address changes. From the host's perspective, the session state remains intact: buffers, congestion window variables, and cryptographic keys are still present in memory. From the transport layer's perspective, however, the identifying tuple has changed.

When the address component of the tuple changes, the transport layer cannot match incoming packets to the existing state entry. The new packets appear to originate from an unknown endpoint. The previous connection state becomes unreachable, and the session is terminated.

The failure is therefore not due to loss of transport state. It arises because the identifier used to index that state is no longer valid. Mobility exposes a structural property of the classical design: identity is defined indirectly through location.

This fragility becomes particularly visible in multihomed scenarios. A host with multiple interfaces may wish to shift traffic from one path to another due to performance or policy reasons. In the classical design, however, such a shift changes the tuple that defines the connection itself. Path selection and session continuity are therefore tightly coupled, even though they conceptually address different concerns.

## Early Architectural Responses

The tension between identity and location has been recognized for decades. As mobility and multihoming became more common, researchers and standards bodies explored solutions at multiple layers of the stack. These efforts differ in mechanism and scope, but they share a common objective: preserving communication continuity when network attachment changes.

### Network-Layer Indirection: Mobile IP

One of the earliest standardized attempts to support mobility was Mobile IP. Rather than redefining transport-layer identity, Mobile IP preserves the existing IP-based binding and introduces indirection at the network layer. A mobile node retains a permanent home address while acquiring a temporary care-of address when attached to a foreign network. A home agent forwards packets destined to the home address to the current care-of address [@rfc3775].

This approach maintains compatibility with unmodified transport protocols, including TCP. From the transport layer’s perspective, the peer continues to communicate with a stable home address. However, this design introduces triangular routing, additional signaling overhead, and reliance on home agents. Mobility is supported by masking location changes rather than decoupling identity from location.

Mobile IP therefore preserves the architectural assumption that IP addresses represent host identity, while compensating for mobility through redirection. It does not alter the fundamental coupling between transport state and the IP-layer identifier.

### A New Namespace: Host Identity Protocol

The Host Identity Protocol (HIP) proposes a more structural revision. Instead of treating IP addresses as both locators and identifiers, HIP introduces a new cryptographic namespace between the network and transport layers. In HIP’s formulation, IP addresses serve solely as routing locators, while host identity is bound to a cryptographic Host Identity (HI) [@nikander2010host].

As articulated in the HIP literature, “in the current IP architecture, the IP addresses assume the dual role of acting both as host identifiers and locators.” HIP seeks to break this duality by giving each host a persistent cryptographic identity independent of network location.

Transport protocols bind to the Host Identity rather than directly to IP addresses. When a host moves and acquires a new address, it updates its peer through HIP signaling without invalidating transport state. This approach makes the separation of identity and location explicit and architectural, rather than incidental.

However, HIP requires widespread deployment of new protocol machinery, including cryptographic identifiers and modified stack behavior. As with many clean-slate refinements to Internet architecture, its adoption has remained limited.

### Transport-Level Multihoming: SCTP

The Stream Control Transmission Protocol (SCTP) represents a transport-layer attempt to accommodate multihoming without redefining IP semantics. Designed with multihoming in mind, SCTP allows a single association to be bound to multiple IP addresses [@rfc4960].

An SCTP endpoint can advertise multiple addresses during association setup, and the peer may use alternate paths if the primary path fails. This supports failover while maintaining a single transport association. Extensions later enabled concurrent multipath transfer.

From an architectural standpoint, SCTP weakens the strict one-to-one relationship between transport connection and IP address pair. An association is no longer uniquely identified by a single four-tuple but may encompass multiple address pairs. However, identity remains tied to the set of IP addresses themselves; SCTP extends the binding rather than replacing it.

Despite its technical strengths, SCTP has seen limited deployment on the public Internet, in part due to middlebox interference and lack of native browser support.

### Concurrent Paths: Multipath TCP

Multipath TCP (MPTCP) extends TCP itself to allow multiple subflows under a single logical connection. Rather than defining a new transport protocol, MPTCP augments TCP with additional options and connection management mechanisms. As described by Barré et al., MPTCP enables hosts to “use several paths possibly through multiple interfaces, to carry the packets that belong to a single connection” [@10.1007/978-3-642-20757-0_35].

An MPTCP connection consists of multiple TCP subflows, each with its own 32-bit sequence space, while the overall connection maintains a separate data sequence number space. This dual-sequence design preserves compatibility with middleboxes, since each subflow appears as a regular TCP connection, while the connection-level sequence space ensures in-order reassembly across paths.

MPTCP directly addresses multihoming and path diversity, but it retains TCP’s reliance on IP address pairs to identify individual subflows. Identity is elevated to the MPTCP connection level via tokens and data sequence numbers, yet the architecture still operates within TCP’s four-tuple foundation.

Importantly, MPTCP must employ coupled congestion control to remain fair to regular TCP flows. Without coupling, multiple subflows would unfairly aggregate bandwidth at shared bottlenecks [@10.1007/978-3-642-20757-0_35]. Thus, architectural flexibility introduces new control challenges.

### Application-Layer Multiplexing: SPDY and Structured Streams

Not all responses to transport rigidity occurred at the network or transport layer. Some addressed related limitations higher in the stack.

SPDY, for example, multiplexes multiple application-layer streams over a single TCP connection. As Wang et al. note, most of SPDY’s performance benefits stem from using “a single TCP connection” to avoid repeated connection setup and reduce idle time [@179787]. By consolidating transfers into one connection, SPDY mitigates head-of-line blocking across independent TCP connections, but it inherits TCP’s single-path semantics. Under high loss, a single connection may degrade performance relative to multiple parallel connections [@179787].

Structured Stream Transport (SST) similarly observes that neither traditional streams nor datagrams adequately support mixed transactional workloads. Ford argues that applications like HTTP face “awkward tradeoffs” between using multiple TCP streams and serializing transactions on persistent connections [@10.1145/1282427.1282421]. SST introduces hierarchical streams that share congestion control context while allowing independent ordering and flow control.

Both SPDY and SST recognize limitations in the classic stream abstraction. However, they operate above IP and do not redefine how transport state is bound to network-layer identifiers. They refine multiplexing and application structure but do not address mobility at the identity layer.

### Synthesis

Across these efforts, a pattern emerges:

- Mobile IP preserves identity-location coupling and adds indirection.
- HIP introduces a new identity namespace, explicitly separating identity from location.
- SCTP and MPTCP extend transport semantics to tolerate multiple addresses.
- SPDY and SST refine multiplexing above TCP but retain underlying bindings.

Each approach relaxes or compensates for the tight coupling between session identity and network location in a different way. Yet none achieved universal deployment across the open Internet. The persistence of the classical 5-tuple model reflects not only technical inertia but also the constraints imposed by middleboxes, incremental deployability, and compatibility requirements.

It is in this context that QUIC emerges: not as the first attempt to decouple identity from location, but as a transport protocol designed from the outset to make that separation explicit while remaining deployable over UDP in today’s Internet.
