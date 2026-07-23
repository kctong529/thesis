## Proposed Solutions

Mobility and multihoming revealed the limits of address-based session identification long before QUIC. The underlying problem is the binding between session identity and network location. Proposed solutions have generally followed one of two strategies. They either preserve the existing binding and conceal address changes from the transport layer, or weaken the binding so that a session can remain valid across different addresses.

The first strategy preserves the traditional address-based transport model. Network-layer approaches, such as mobile IP, maintain the appearance of a stable IP address through indirection [@rfc3775]. The second strategy changes how identity or transport state relates to network addresses. Identity-layer approaches, such as HIP, introduce a separate namespace for host identity [@nikander2010host], while transport-layer approaches, such as SCTP and multipath TCP, allow one transport association or connection to use multiple addresses or paths [@rfc4960; @10.1007/978-3-642-20757-0_35]. Application-layer approaches do not alter the identity-location coupling itself but compensate for transport limitations above the transport interface [@179787].

These approaches handle continuity at different layers and require different changes to endpoints and network infrastructure. Each approach addresses communication continuity when addresses change or when several addresses are available. The following subsections examine how they modify the identity-location coupling or compensate for its effects, and what restricted their broader deployment on the public Internet. This history forms the architectural background for QUIC.

### Network-Layer Indirection: Mobile IP

Mobile IP preserves a stable IP address even when a host changes its network attachment point [@rfc3775]. A mobile node retains a permanent home address and obtains a temporary care-of address in the visited network. A home agent receives packets sent to the home address and forwards them to the current care-of address.

The transport layer continues to observe the home address. Therefore, a protocol such as TCP can retain the same four-tuple even though the mobile node now receives packets through another network. Mobile IP preserves session continuity because it hides the location change below the transport layer and does not require a separate session identifier.

Existing transport protocols can continue to function without direct support for mobility. However, the required indirection depends on home-agent infrastructure and additional mobility signalling. Packet delivery may also become indirect. For example, a correspondent host may send packets first to the home network, after which the home agent forwards them to the current care-of address. Return traffic may travel directly from the mobile node to the correspondent host, so the two directions follow different routes.

Mobile IP becomes more difficult to deploy across administrative domains. The mobile node, home network, access network, and correspondent node may belong to different operators, while the mobility mechanism must remain available across all of them. Mobile IP reduces the effect of the identity-location coupling through network-layer indirection, but the transport connection still depends on a home address that appears stable to the transport layer.

### A New Namespace: Host Identity Protocol

HIP addresses the identity-location coupling by assigning host identity to a separate cryptographic namespace [@nikander2010host]. IP addresses remain routing locators, while a cryptographic host identity identifies the communicating host. HIP introduces this additional namespace between the network and transport layers.

Transport state can then refer to the host identity instead of one fixed IP address. If a host moves and obtains a new address, it can inform its peer through HIP signalling. The peer can then associate the new locator with the same host identity, so the transport state does not need to depend directly on the new address.

The separate host identity namespace requires support beyond a single endpoint. Both peers must support HIP before they can use the new identifier, and the communication path must permit the additional HIP traffic. Middleboxes that expect conventional address-based communication may interfere with HIP traffic under these conditions. These deployment requirements have limited the use of HIP on the public Internet.

HIP was one of the early protocols to introduce a separate entity for host identity. Its deployment remained limited, but the host identity can remain stable while the IP address changes, which decouples identity from network location. The protocol provides a direct example of identity that does not depend on the current IP address.

### Transport-Level Multihoming: SCTP

SCTP places multihoming support directly in the transport layer [@rfc4960]. One SCTP association can include several IP addresses for the communicating endpoints. The association can remain valid across several address pairs without network-layer indirection or a separate host identity namespace.

During association setup, an SCTP endpoint can provide its peer with a list of available IP addresses. The peer can use these addresses as alternative paths within the same association. If the primary path fails, it can select another known address and continue the communication without a new transport association. Later extensions also added support for concurrent multipath transfer.

An SCTP association is not limited to one four-tuple and may span several address pairs. This capability weakens the identity-location coupling because a change between the known addresses does not change the association itself. However, the set of addresses still forms part of the association. SCTP extends the address-based model without introducing an address-independent session identifier.

The known address set still limits mobility. Failover can preserve the association as long as another known address remains available, but an arbitrary new address does not automatically refer to the existing association. SCTP reduces the effect of the identity-location coupling, but session identity still depends on a known set of IP addresses.

SCTP remains uncommon on the public Internet. Middleboxes may block or mishandle SCTP traffic, application support remains limited, and browsers do not provide native SCTP access. Applications cannot generally rely on SCTP even when both endpoints could benefit from multihoming. The protocol weakens the identity-location coupling at the transport layer, but its practical benefits depend on support from endpoints, applications, and network infrastructure.

### Multipath TCP

Multipath TCP extends TCP so that one logical connection can use more than one network path [@10.1007/978-3-642-20757-0_35]. An MPTCP connection is formed from multiple TCP flows, called subflows, which may use different interfaces and address pairs. Each subflow has its own source and destination addresses and port numbers and appears on the network as a regular TCP connection. The logical connection is no longer restricted to one address pair.

Additional MPTCP state allows several subflows to operate as one logical connection. Each subflow maintains its own TCP sequence space, while the MPTCP connection maintains a separate data sequence number space across the subflows. This connection-level sequence space maps data from the individual subflows into one ordered byte stream. The application sees a single connection even when data is carried over several network paths.

A multihomed host can establish subflows through different network interfaces. For example, one subflow may use Wi-Fi while another uses a cellular interface, without exposing separate connections to the application. The logical connection can then remain active across different address pairs, which weakens the identity-location coupling at the connection level.

The identity-location coupling still remains at the level of the individual subflows. Each subflow is identified by its own four-tuple and remains bound to a particular address pair. MPTCP associates these address-bound subflows with the same logical connection, but it does not remove address-based identification from the underlying TCP flows. MPTCP weakens the coupling at the logical connection level without introducing an address-independent identifier for each subflow.

Several subflows may also compete for capacity at the same network bottleneck. If each subflow applied congestion control independently, one MPTCP connection could obtain an unfair share of the available capacity. MPTCP uses coupled congestion control to coordinate the subflows and limit this effect [@10.1007/978-3-642-20757-0_35]. The use of multiple paths requires congestion control to be coordinated across subflows that conventional TCP would treat as separate connections.

MPTCP has seen practical deployment, but its use remains limited compared with conventional TCP [@shreedhar2022longitudinalviewadoptionmultipath]. Both endpoints must support MPTCP, and middleboxes may interfere with the TCP extensions used by the protocol [@shreedhar2022longitudinalviewadoptionmultipath]. Measurements of Internet traffic found that MPTCP accounted for only a small share of observed traffic despite growth in its deployment [@shreedhar2022longitudinalviewadoptionmultipath]. Applications cannot assume that MPTCP support is available for mobility or multihoming on the public Internet.

### Application-Layer Workaround: SPDY

SPDY changes how an application uses an existing transport connection without changing the identity of that connection. It allows multiple application-layer streams to share one TCP connection [@179787]. The underlying TCP connection remains identified by its source and destination addresses and port numbers.

SPDY does not weaken the identity-location coupling itself. A change of network address still affects the TCP connection in the same way as without SPDY, regardless of how many application streams share it. Its relevance here is that application-layer changes alone cannot preserve transport identity across a change of network location.

### Synthesis

The reviewed approaches show several ways to respond to the coupling between the session identity and the network location. Mobile IP preserves IP-based identity and hides mobility through network-layer indirection. HIP introduces a separate namespace for host identity. SCTP and MPTCP extend transport protocols so that one association or logical connection can use multiple addresses or paths. SPDY improves application-level communication over TCP without changing the transport-layer identifier.

A central difference is what remains stable when the network location changes. Mobile IP keeps the home address stable and redirects traffic to the current location, while HIP introduces a host identity that remains independent of the IP address. SCTP and MPTCP move part of this stability into the transport layer, where an association or logical connection can continue across more than one address pair. SPDY does not provide such stability because the underlying TCP connection remains tied to its four-tuple.

These designs also differ in what they require for deployment. Mobile IP requires mobility infrastructure, HIP requires support for a separate identity layer, and SCTP depends on transport support that is not generally available on the public Internet. MPTCP remains closer to conventional TCP, but both endpoints must support its extensions and the individual subflows remain address-bound. Approaches that change the identity-location relationship more directly usually require support below the application layer.

These earlier proposals establish the architectural context for later transport designs. Session continuity depends on how identity is represented, where the required support is placed in the protocol stack, and whether that support can be deployed in practice. The next section introduces QUIC and examines its approach to these architectural constraints.
