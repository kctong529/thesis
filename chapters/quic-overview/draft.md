## From Application Communication to HTTP

Transport protocols provide mechanisms such as reliability, congestion control, and ordered delivery, but they do not by themselves define the meaning of the data exchanged between applications. Application-layer protocols are therefore needed to specify how messages are structured, how requests and responses are interpreted, and how communicating endpoints assign meaning to exchanged data [@kurose2025].

On the web, that role is performed by the Hypertext Transfer Protocol (HTTP). HTTP is a stateless application-level protocol for distributed hypertext information systems and defines a request-response model in which a client sends a request and a server returns a response containing status information, metadata, and, when appropriate, a representation of the requested resource [@rfc9110]. HTTP therefore provides the semantic structure required for web communication, while the underlying transport protocol provides the mechanisms needed to carry that communication between endpoints [@kurose2025].

Early versions of HTTP were developed for a web environment in which clients typically retrieved a document together with a limited number of associated resources. As the web evolved into a platform for interactive and media-rich applications, the number and concurrency of requests increased substantially. Modern web pages often require the transfer of many objects, including scripts, style sheets, images, fonts, and asynchronous application data. The resulting communication pattern placed growing pressure on the efficiency of the underlying transport layer [@kurose2025].

HTTP/1.1 improved performance through persistent connections. However, browsers still commonly opened multiple parallel Transmission Control Protocol (TCP) connections to the same origin. HTTP/2 introduced multiplexing over a single TCP connection, yet it continued to inherit TCP’s ordered byte-stream semantics. Packet loss at the TCP layer could therefore delay the delivery of otherwise independent application data. Transport-level head-of-line blocking remained a significant limitation. QUIC emerged in response to these transport limitations, and HTTP/3 was subsequently defined as HTTP over QUIC [@kurose2025; @rfc9000].

## QUIC and HTTP/3 in the Protocol Stack

QUIC is a general-purpose transport protocol standardized by the Internet Engineering Task Force (IETF) in RFC 9000 [@rfc9000]. Although QUIC is often discussed in the context of web traffic, the protocol is not limited to HTTP/3. More generally, QUIC provides transport services that include connection establishment, reliability, congestion control, stream multiplexing, and path management [@rfc9000; @rfc9002].

HTTP/3 is the first standardized version of HTTP that operates over QUIC rather than directly over TCP. Earlier versions of HTTP relied on TCP for reliable transport and on a separate security layer for encryption. In the HTTP/3 stack, QUIC provides the transport substrate directly, while HTTP continues to provide request-response semantics at the application layer [@rfc9110; @rfc9000].

Within the scope of this thesis, the significance of HTTP/3 lies primarily in the fact that it depends on QUIC. The analysis in the following subsections therefore concentrates on QUIC as a transport architecture rather than on HTTP semantics.

## Connection Identifiers and Path Management

The QUIC feature most directly relevant to mobility and multihoming is the separation between connection identity and the current address pair. In classical TCP communication, packets are associated with connection state through the source and destination addresses together with their port numbers. In QUIC, by contrast, packets may be associated with connection state through an explicit connection identifier carried in the packet header [@rfc9000].

Since the connection identifier is independent of the current network-layer address pair, a QUIC connection does not depend exclusively on the continued use of one address pair. QUIC can therefore preserve connection continuity across address changes in a manner that is not available in the classical TCP model. In architectural terms, QUIC distinguishes between an ongoing connection and the particular network path currently used to carry packets [@rfc9000].

RFC 9000 also defines path validation and migration-related behavior. Before a new path is used for sustained communication, the endpoint may validate that path. Path validation is necessary, since address change cannot be treated solely as a routing event. The transport protocol must also determine whether the new path is usable and whether packets received on that path should be associated with the existing connection [@rfc9000].

Connection identifiers and path validation are therefore central to this thesis. In the traditional model, a change in address immediately threatens connection continuity, as transport identity is derived from address information. In QUIC, by contrast, address change becomes a transport event that may be detected, validated, and, under appropriate conditions, accommodated through explicit protocol mechanisms [@rfc9000].

## QUIC as a UDP-based Secure Transport

The transport properties described above are supported by broader architectural choices in QUIC. One major difference from TCP is that QUIC operates over the User Datagram Protocol (UDP) [@rfc9000]. UDP is a minimal transport protocol that provides port-based delivery between applications, but does not by itself provide connection establishment, reliability, retransmission, congestion control, or ordered delivery. In the traditional Internet stack, those functions are typically associated with TCP rather than UDP [@kurose2025].

The use of UDP allows QUIC to implement transport functionality in user space rather than in operating system kernels. User-space deployment avoids the need to introduce new transport behavior directly into kernel TCP implementations and allows protocol evolution to proceed more rapidly [@rfc9000]. QUIC therefore uses UDP as a substrate, while implementing the more complex transport functions within the QUIC protocol itself.

The use of UDP does not imply that QUIC provides only an unreliable datagram service. QUIC implements reliability, acknowledgments, retransmission behavior, congestion control, and ordered delivery within the protocol itself [@rfc9000; @rfc9002]. QUIC therefore retains many transport functions traditionally associated with TCP while altering the context in which those functions are implemented and deployed.

Another major difference lies in the integration of security into the transport protocol. QUIC incorporates cryptographic negotiation into connection establishment rather than treating encryption as a separate layer placed above transport [@rfc9000]. Transport setup and session protection therefore form part of a single protocol framework.

## Streams and Multiplexing

QUIC differs from TCP in connection establishment, path management, and the structure of data delivery. TCP provides a single ordered byte stream per connection. QUIC, by contrast, provides multiple streams within a single connection, with separate ordering and flow control at the stream level [@rfc9000].

The stream abstraction is significant for HTTP/3, as independent request-response exchanges can be placed on separate streams rather than serialized through a single transport-level byte stream. Packet loss may still affect congestion control and retransmission behavior at the connection level, but loss affecting one stream need not block data delivery on other streams in the same manner as in TCP-based transport. Stream multiplexing is therefore a major source of the improved application behavior associated with QUIC-based transport [@rfc9000].

Within the scope of this thesis, however, streams are not the primary focus. Stream multiplexing is central to QUIC performance and to the design of HTTP/3, but the questions of mobility and multihoming depend more directly on how QUIC identifies and maintains connections across changing network paths.

## Relevance to Mobility and Multihoming

The relevance of QUIC to the present thesis follows from the way the protocol treats connection continuity under address change. Mobility and multihoming are no longer immediate connection-terminating events in the same way as in the classical TCP model. Instead, address change becomes part of path management within the transport protocol itself [@rfc9000].

The resulting protocol behavior nevertheless depends on factors such as path validation, congestion state, endpoint policy, and middlebox behavior. QUIC does not eliminate the operational complexity associated with mobility and multihoming, but it changes the architectural basis on which those problems are handled. Loss detection and congestion control remain important parts of that behavior, particularly when communication shifts onto a new path [@rfc9002].

Section 4 examines those mechanisms in greater detail. The main focus is on how QUIC validates new paths, manages connection state across address changes, and balances architectural flexibility against operational and deployment constraints.
