## Proposed Solutions

The limitations exposed by mobility and multihoming have been recognized for decades. In response, researchers have proposed solutions at different layers of the stack. Some introduced indirection at the network layer. Others redefined identity through new namespaces or extended transport and application semantics. Although these approaches differ in mechanism, they can be understood as successive attempts to relax or circumvent the binding between session identity and network location.

### Network-Layer Indirection: Mobile IP

One of the earliest standardized attempts to support mobility was Mobile IP. Rather than redefining transport-layer identity, Mobile IP preserves the existing IP-based binding and introduces indirection at the network layer. A mobile node retains a permanent home address while acquiring a temporary care-of address when attached to a foreign network. A home agent forwards packets destined to the home address to the current care-of address [@rfc3775].

This approach maintains compatibility with unmodified transport protocols, including TCP. From the transport layer's perspective, the peer continues to communicate with a stable home address. However, this design introduces triangular routing, additional signaling overhead, and reliance on home agents. Mobility is supported by masking location changes rather than decoupling identity from location.

Mobile IP therefore preserves the architectural assumption that IP addresses represent host identity, while compensating for mobility through redirection. It does not alter the fundamental coupling between transport state and the IP-layer identifier. \hfill \break

Rather than preserving the IP address as the sole identifier through indirection, other proposals questioned whether IP addresses should serve as identifiers at all.

### A New Namespace: Host Identity Protocol

The Host Identity Protocol (HIP) proposes a more structural revision. Instead of treating IP addresses as both locators and identifiers, HIP introduces a new cryptographic namespace between the network and transport layers. In HIP's formulation, IP addresses serve solely as routing locators, while host identity is bound to a cryptographic Host Identity (HI) [@nikander2010host].

Transport protocols bind to the Host Identity rather than directly to IP addresses. When a host moves and acquires a new address, it updates its peer through HIP signaling without invalidating transport state. This approach makes the separation of identity and location explicit and architectural, rather than incidental.

However, HIP requires deployment of new protocol machinery at both endpoints and introduces compatibility challenges with existing middleboxes, including cryptographic identifiers and modified stack behavior. As with many clean-slate refinements to Internet architecture, its adoption has remained limited. \hfill \break

At the transport layer, other approaches avoid introducing a new namespace and instead extend existing protocols.

### Transport-Level Multihoming: SCTP

The Stream Control Transmission Protocol (SCTP) represents a transport-layer attempt to accommodate multihoming without redefining IP semantics. Designed with multihoming in mind, SCTP allows a single association to be bound to multiple IP addresses [@rfc4960].

An SCTP endpoint can advertise multiple addresses during association setup, and the peer may use alternate paths if the primary path fails. This supports failover while maintaining a single transport association. Extensions later enabled concurrent multipath transfer.

From an architectural standpoint, SCTP weakens the strict one-to-one relationship between transport connection and IP address pair. An association is no longer uniquely identified by a single four-tuple but may span multiple address pairs. However, identity remains tied to the set of IP addresses themselves. SCTP extends the binding rather than replacing it.

Despite its technical strengths, SCTP has seen limited deployment on the public Internet, in part due to middlebox interference and lack of native browser support. \hfill \break

A closely related approach extends TCP itself while preserving wire compatibility.

### Multipath TCP

Multipath TCP (MPTCP) extends TCP itself to allow multiple subflows under a single logical connection. Rather than defining a new transport protocol, MPTCP augments TCP with additional options and connection management mechanisms. As described by Barré et al., MPTCP enables hosts to “use several paths possibly through multiple interfaces, to carry the packets that belong to a single connection” [@10.1007/978-3-642-20757-0_35].

An MPTCP connection consists of multiple TCP subflows, each with its own 32-bit sequence space, while the overall connection maintains a separate data sequence number space. This dual-sequence design preserves compatibility with middleboxes, since each subflow appears as a regular TCP connection, while the connection-level sequence space ensures in-order reassembly across paths.

MPTCP directly addresses multihoming and path diversity, but it retains TCP's reliance on IP address pairs to identify individual subflows. Connection-level tokens enable additional subflows to join an existing MPTCP connection, while a separate data sequence number space ensures coherent reassembly across subflows.

Importantly, MPTCP must employ coupled congestion control to remain fair to regular TCP flows. Without coupling, multiple subflows would unfairly aggregate bandwidth at shared bottlenecks [@10.1007/978-3-642-20757-0_35]. Thus, architectural flexibility introduces new control challenges.

### Application-Layer

Not all responses sought to modify the network or transport layer. Some addressed related limitations at the application layer instead.

SPDY, for example, multiplexes multiple application-layer streams over a single TCP connection. As Wang et al. note, most of SPDY's performance benefits stem from using “a single TCP connection” to avoid repeated connection setup and reduce idle time [@179787]. By consolidating transfers into one connection, SPDY mitigates application-level head-of-line blocking across multiple TCP connections, but it inherits TCP's single-path semantics. Under high loss, a single connection may degrade performance relative to multiple parallel connections [@179787].

Structured Stream Transport (SST) similarly observes that neither traditional streams nor datagrams adequately support mixed transactional workloads. Ford argues that applications like HTTP face “awkward tradeoffs” between using multiple TCP streams and serializing transactions on persistent connections [@10.1145/1282427.1282421]. SST introduces hierarchical streams that share congestion control context while allowing independent ordering and flow control.

Both SPDY and SST recognize limitations in the classic stream abstraction. However, they operate above IP and do not redefine how transport state is bound to network-layer identifiers. These approaches improve performance and application structure but do not fundamentally change how transport sessions are identified in the network.

### Synthesis

Across these efforts, a pattern emerges:

- Preserve IP-based identity through indirection, as in Mobile IP
- Introduce a separate identity namespace, as in HIP
- Extend transport protocols to support multiple addresses, as in SCTP and MPTCP
- Work around transport limitations at the application layer, as in SPDY and SST

These approaches differ not only in mechanism but in the architectural layer at which they intervene. Each approach relaxes or compensates for the tight coupling between session identity and network location in a different way. None achieved broad, general-purpose deployment across the public Internet. The persistence of the classical four-tuple model reflects not only technical inertia but also the constraints imposed by middleboxes, incremental deployability, and compatibility requirements.

These limitations and trade-offs provide the context in which QUIC was developed. Rather than being the first attempt to decouple identity from location, QUIC is a transport protocol designed from the outset to make that separation explicit while remaining incrementally deployable over UDP in the Internet of today.
