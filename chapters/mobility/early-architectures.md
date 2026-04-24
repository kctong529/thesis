## Proposed Solutions

The limitations exposed by mobility and multihoming have been recognized for decades. Since the problem arises from the binding between the session identity and the network location, proposed solutions have generally followed one of two strategies: either preserve the existing binding and hide address changes, or introduce mechanisms that weaken the binding itself. Network-layer approaches, such as mobile IP, preserve the stable IP address abstraction through indirection [@rfc3775]. Identity-layer approaches, such as HIP, introduce a separate namespace for host identity [@nikander2010host]. Transport-layer approaches, such as SCTP and multipath TCP, extend the connection abstraction to support multiple addresses or paths [@rfc4960; @10.1007/978-3-642-20757-0_35]. Application-layer approaches compensate for transport limitations above the transport interface [@179787].

These proposals differ in the layer where they intervene, but they address the same architectural tension. Each approach attempts to preserve communication continuity when the address information associated with a session changes or when several addresses are available. The following subsections review these approaches in order to show why mobility and multihoming have remained difficult to support in the open Internet.

### Network-Layer Indirection: Mobile IP

Mobile IP represents the first strategy: it preserves the existing IP-based identity model and hides mobility through network-layer indirection [@rfc3775]. A mobile node retains a permanent home address even when it attaches to a foreign network. At the foreign network, the mobile node receives a temporary care-of address. A home agent then forwards packets from the home address to the current care-of address.

This mechanism allows unmodified transport protocols, such as TCP, to continue to use the home address as the apparent peer address. From the transport-layer perspective, the connection still appears to use a stable IP-layer identifier. Therefore, the address change does not directly invalidate the four-tuple. Mobile IP supports mobility through an apparently stable home address without separating identity from location.

This design choice explains both the strength and the limitation of mobile IP. The strength is its compatibility with existing transport protocols, since TCP does not need to interpret mobility events. The limitation is that mobility support depends on home-agent infrastructure, additional mobility signalling, and possible triangular routing. These requirements make deployment difficult across administrative domains, especially in the open Internet where end hosts, access networks, and service providers are not controlled by one operator. Hence, mobile IP compensates for mobility within the network layer, but the transport layer still relies on a stable IP address as the connection identifier.

### A New Namespace: Host Identity Protocol

HIP represents a more structural response to the identity-location problem. Instead of treating IP addresses as both locators and identifiers, HIP introduces a cryptographic namespace between the network and transport layers [@nikander2010host]. In the HIP formulation, IP addresses serve as routing locators, while host identity is bound to a cryptographic host identity.

This design changes the identifier used by the transport layer: transport state is associated with the host identity rather than directly with an IP address. When a host moves and receives a new address, the host can update its peer through HIP signalling without invalidating the transport state. Therefore, the separation of identity and location becomes an explicit part of the architecture.

This explicit separation provides a cleaner architectural model, but it also requires endpoints and network environments to support new protocol machinery. HIP requires new protocol support at both endpoints and changes the assumptions of the existing stack. It also introduces compatibility challenges with middleboxes that expect conventional address-based communication. As a result, HIP provides a clean architectural solution to the identity-location problem, but its adoption has remained limited in the open Internet.

Although HIP did not achieve broad deployment, its design illustrates an important architectural direction: connection continuity can be improved when the transport layer is no longer tied directly to IP addresses. Later transport designs, including QUIC, address the same problem in a more deployable form by separating connection identity from the current address pair.

### Transport-Level Multihoming: SCTP

SCTP represents a transport-layer response to multihoming [@rfc4960]. It does not redefine IP semantics or introduce a new host identity namespace. Instead, SCTP extends the transport association so that one association can include multiple IP addresses. This approach places multihoming support inside the transport layer and avoids both network-layer indirection and a separate identity layer.

An SCTP endpoint can advertise multiple addresses during association setup. The peer can then use an alternate path if the primary path fails. This mechanism supports failover while it preserves a single transport association. Later extensions also added support for concurrent multipath transfer.

This design weakens the strict one-to-one relationship between a transport connection and an IP address pair. An SCTP association does not need to remain limited to one four-tuple and may span several address pairs. However, the association is still defined by a known set of IP addresses. Therefore, SCTP extends the address-based binding, but it does not replace that binding with an address-independent connection identifier.

This distinction explains why SCTP only partially addresses the identity-location problem. SCTP can preserve an association across the failure of one path, provided that another advertised address remains available. The association can span multiple IP addresses, but those addresses still define the association. Thus, the protocol improves multihoming support, but it does not fully separate transport identity from the network location.

The deployment history of SCTP also illustrates the difficulty of transport-layer change. Despite its technical support for multihoming, SCTP has seen limited deployment on the public Internet. Middlebox interference, limited application adoption, and lack of native browser support have restricted its general use. Hence, SCTP demonstrates that transport-layer support for multiple addresses is not sufficient by itself when deployment compatibility remains weak.

### Multipath TCP

MPTCP extends TCP to support multiple subflows under a single logical connection. It does not replace TCP with a new transport protocol. Instead, it augments TCP with additional options and connection-management mechanisms. MPTCP allows packets from one connection to use several paths, possibly through multiple interfaces [@10.1007/978-3-642-20757-0_35].

An MPTCP connection consists of multiple TCP subflows. Each subflow has its own sequence space and appears on the network as a regular TCP connection. At the same time, the overall MPTCP connection maintains a separate data sequence number space. This additional sequence space allows data from multiple subflows to be reassembled into one ordered byte stream.

This structure makes MPTCP relevant to multihoming. A host can add subflows through different interfaces and transfer data over multiple paths under one logical connection. Although the network sees several TCP subflows, the application sees one connection. As a result, MPTCP weakens the dependence of the application-level connection on a single path.

The limitation of MPTCP is that it does not remove address-based identification. Each subflow remains a TCP connection with its own source and destination IP addresses and port numbers. Connection-level tokens and data sequence numbers allow these subflows to belong to the same MPTCP connection, but the subflows themselves are still tied to address pairs. Therefore, MPTCP extends the classical TCP model without replacing it with an address-independent connection identifier.

This extension also introduces control challenges. MPTCP must use coupled congestion control so that multiple subflows do not unfairly aggregate bandwidth at shared bottlenecks [@10.1007/978-3-642-20757-0_35]. The protocol gains flexibility across paths, but it must also coordinate congestion behavior across those paths. MPTCP shows that support for multiple paths requires connection management and careful control of network resource use.

### Application-Layer Workaround: SPDY

Not all responses to transport limitations modify the network or transport layer. Some approaches operate at the application layer and compensate for limitations exposed by the underlying transport service. These approaches can improve performance or application structure, but they do not change the identifier used by the transport layer.

SPDY illustrates this kind of workaround. It multiplexes multiple application-layer streams over a single TCP connection and reduces repeated connection setup by consolidating transfers into one connection [@179787]. This design improves application-level efficiency and reduces idle time. However, the underlying transport remains one TCP connection, so SPDY inherits the single-path semantics of TCP. Under high loss, this single-connection structure may perform worse than multiple parallel TCP connections.

This example shows the limit of application-layer responses in the context of mobility and multihoming. Application-layer mechanisms can change how applications organize communication over an existing transport service. They cannot by themselves separate transport identity from the network location. The transport connection remains bound to the address and port information of the underlying protocol, so the identity-location problem is still at the transport and network boundary.

### Synthesis

The reviewed approaches show several ways to respond to the coupling between the session identity and the network location. Mobile IP preserves IP-based identity and hides mobility through network-layer indirection. HIP introduces a separate namespace for host identity. SCTP and MPTCP extend transport protocols so that one association or logical connection can use multiple addresses or paths. SPDY improves application-level communication over TCP without changing the transport-layer identifier.

These approaches differ in mechanism and architectural layer, but they share a common motivation. Each one attempts to preserve communication continuity when address information changes or when several addresses are available. Their differences lie in where the problem is handled. Network-layer indirection hides the address change. Identity-layer mechanisms introduce a new identifier. Transport-layer mechanisms extend the connection abstraction. Application-layer mechanisms compensate above the transport interface.

The comparison also shows a recurring trade-off. Approaches that provide a cleaner separation of identity and location often require new protocol machinery or new deployment assumptions. Approaches that remain compatible with existing infrastructure often preserve part of the original address-based model. This trade-off helps explain why none of the reviewed approaches achieved broad, general-purpose deployment across the public Internet.

Hence, the persistence of the classical four-tuple model reflects more than technical inertia. Middleboxes, operating system support, browser adoption, administrative boundaries, and incremental deployability all constrain protocol change. These constraints form the context for QUIC. QUIC is not the first attempt to weaken the coupling between identity and location, but it combines explicit connection identifiers, transport-layer path management, and deployment over UDP. This combination makes QUIC a practical transport-layer response to address change within the deployed Internet.
