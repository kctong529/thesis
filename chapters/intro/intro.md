
In the traditional Internet architecture, a transport connection is identified by a pair of Internet Protocol (IP) addresses and port numbers. That identification model assumes that endpoint addresses remain stable throughout the lifetime of the connection.

In many contemporary network environments, however, address stability cannot be assumed. When a host changes its point of attachment to the network and acquires a new IP address, the transport layer can no longer associate subsequent packets with the existing connection state. The session is therefore terminated even though the communicating application may remain active.

Address change becomes problematic in two related but distinct situations. In mobility, a host typically uses one IP address at a time, but the address may change while communication is ongoing. In multihoming, by contrast, a host may have multiple IP addresses available simultaneously, for example through different network interfaces. The set of usable addresses may also change over time, so the two phenomena may overlap in practice.

Mobility and multihoming therefore expose a broader architectural problem. In the classical model, session identity is tied implicitly to network location.

The coupling between identity and location arises from two features of the Internet architecture. Communication state is maintained at the endpoints, and ongoing exchanges are identified through address information carried in packets.

At a basic level, Internet communication extends across multiple packet transmissions. To sustain communication across those transmissions, endpoints maintain state describing what has been sent, received, and acknowledged. The network layer itself does not maintain comparable state. In accordance with the end-to-end principle [@saltzer1984end], reliability and ordering are implemented at the endpoints, while the network provides only best-effort delivery.

Since the network does not track active sessions, endpoints must determine how arriving packets relate to stored communication state. In the classical Internet architecture, that association is derived from the source and destination IP addresses together with their port numbers. Session identity is therefore derived from network-layer location.

Early Internet specifications do not define the relationship between identity and location as an explicit design principle. The relationship nevertheless follows from the implementation of transport protocols. In the Transmission Control Protocol (TCP), for example, connection state is associated with the combination of source and destination IP addresses and port numbers. As long as the values remain stable, packets can be matched to the correct session state. Once the values change, later packets are treated as belonging to a different connection. The mechanism is simple and efficient, but it depends on stable network attachment.

Contemporary deployment environments often lack the required degree of stability. Hosts may be multihomed, address translation devices may rewrite source addresses and ports, and routing conditions may change independently of application behavior. Under those conditions, the correspondence between the communicating entity and its current network location becomes fragile. A change in address may then break the association between packets and existing transport state, even though communication at the application level continues.

The resulting tension between communication continuity and address dependence has been recognized for decades. Researchers have proposed architectural responses at different layers of the stack. Those responses include network-layer indirection mechanisms such as Mobile IP, identity-location separation approaches such as the Host Identity Protocol (HIP), transport-layer extensions such as the Stream Control Transmission Protocol (SCTP) and Multipath TCP (MPTCP), and application-layer techniques that work around transport limitations. Despite considerable technical merit, the proposed approaches have faced significant deployment and compatibility constraints in the open Internet.

QUIC was developed in the context of those earlier efforts. Standardized by the Internet Engineering Task Force (IETF) in RFC 9000 [@rfc9000], QUIC was designed in part to address limitations of traditional transport protocols, including reliance on IP address based connection identification and the difficulty of evolving transport behavior in the deployed Internet.

Unlike TCP, QUIC runs over the User Datagram Protocol (UDP), which permits user-space implementation and allows the protocol to evolve more rapidly. QUIC also incorporates Transport Layer Security (TLS) 1.3 directly into its design, so that encryption is always present and connection establishment combines transport and cryptographic negotiation.

The central feature of QUIC is the separation between connection identity and the current address pair. QUIC does not associate connection state solely with the IP address and port pair. Instead, QUIC uses an explicit connection identifier carried in the packet header. Because the identifier is independent of network-layer addressing, packets can continue to be associated with an existing connection even when the host's IP address changes.

QUIC also supports multiplexed streams within a single connection. Stream multiplexing reduces head-of-line blocking and improves application performance, but stream multiplexing is analytically separate from the problems of mobility and multihoming considered here.

This thesis examines how QUIC accommodates mobility and multihoming by separating connection identity from network location. The analysis focuses on the mechanisms that support connection migration, the interaction between those mechanisms and devices such as Network Address Translation (NAT) middleboxes and load balancers, and the effectiveness and limitations of the design in realistic deployment scenarios.

The remainder of the thesis is organized as follows. Section 2 presents the architectural background and defines the identity-location problem in greater detail. Section 3 provides an overview of QUIC and HTTP/3. Section 4 examines connection migration mechanisms and related extensions. Section 5 presents an exploratory evaluation. Section 6 concludes the thesis.
