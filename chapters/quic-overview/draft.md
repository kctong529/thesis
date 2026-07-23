
QUIC is the transport protocol examined in the remainder of this thesis. HTTP and HTTP/3 are introduced here only as the deployment context that motivated QUIC development. After that, the section focuses on QUIC itself: its UDP-based deployment model, secure transport design, connection identifiers, packet structure, and stream abstraction.

## Evolution of HTTP as Motivation for QUIC

Transport protocols provide mechanisms such as reliability, congestion control, and ordered delivery. They do not define the meaning of the data exchanged between applications. Application-layer protocols specify the structure of messages, the interpretation of requests and responses, and the semantics assigned to exchanged data [@kurose2025].

In Internet applications, this role is often performed by the hypertext transfer protocol (HTTP). HTTP defines a request-response model in which a client sends a request and a server returns a response with status information, metadata, and, when appropriate, a representation of the requested resource [@rfc9110]. HTTP provides the semantic structure for many application-layer exchanges, while the transport protocol carries the data between endpoints [@kurose2025].

Early versions of HTTP were developed for a web environment with relatively simple pages and a limited number of associated resources. As web applications became more interactive and media-rich, the number of concurrent resource transfers increased. Modern web pages may require scripts, style sheets, images, fonts, and asynchronous application data to be transferred during the same page load. These concurrent transfers increased the demands placed on the underlying transport protocol [@kurose2025].

The increasing number of concurrent web transfers exposed limitations in how HTTP used TCP. HTTP/1.1 often relied on several parallel TCP connections, while HTTP/2 concentrated multiple application streams into one connection. In HTTP/2, all streams still share the same underlying TCP byte stream. If TCP has to wait for a missing segment, delivery of data for other streams can also be delayed. These limitations were among the reasons for developing QUIC. HTTP/3 subsequently adopted QUIC as its transport protocol [@kurose2025; @rfc9000].

HTTP/3 is mainly relevant to this thesis as a deployment driver for QUIC. The following sections do not examine HTTP semantics in detail. The focus is instead on the QUIC transport mechanisms that separate connection identity from the current address pair.

## QUIC as a UDP-based Secure Transport

QUIC is a general-purpose transport protocol standardized by the Internet Engineering Task Force (IETF) in RFC 9000 [@rfc9000]. Unlike TCP, QUIC operates over the user datagram protocol (UDP). UDP is connectionless and transfers data as individual messages called datagrams [@kurose2025]. Each datagram is handled independently, without an established transport connection between the endpoints. UDP does not maintain connection state or provide reliability, loss recovery, congestion control, flow control, or a stream abstraction [@kurose2025]. UDP can also be used with IP broadcast and multicast since no separate transport connection has to be established with each receiver.

QUIC builds a connection abstraction on top of these independent UDP datagrams. It uses UDP as a substrate, while the more complex transport functions are implemented within the QUIC protocol itself. Unlike TCP, whose implementation is traditionally part of the operating system kernel [@kurose2025], QUIC implementations can provide these functions in user space as part of the software used by an application. This avoids the need to add new QUIC-specific transport behavior directly to the operating system kernel. QUIC support can instead be distributed with application software, so deployment and protocol evolution depend less on operating system updates.

The QUIC endpoints maintain the state needed to associate successive datagrams with the same connection. QUIC also provides acknowledgments, loss recovery, congestion control, flow control, packet numbering, and multiple streams, with ordered delivery within each stream [@rfc9000; @rfc9002]. From the perspective of UDP, these packets remain individual datagrams; their association with an ongoing connection is maintained by QUIC.

QUIC integrates the TLS 1.3 handshake into connection establishment [@rfc9000]. During the handshake, the endpoints establish cryptographic keys and negotiate transport parameters. Most QUIC packet contents are protected after the handshake, while selected header fields remain visible for packet processing and connection identification. The connection includes both transport state and the cryptographic context established during the handshake. Figure \ref{fig:quic-stack} shows the resulting position of QUIC in the protocol stack.

\begin{center}
\includegraphics[width=0.3\linewidth,keepaspectratio]{stack.png}
\captionof{figure}{QUIC protocol stack}
\label{fig:quic-stack}
\end{center}

UDP still uses source and destination addresses and ports to deliver QUIC datagrams. QUIC maintains its connection state above this address pair and defines explicit connection identifiers that can refer to that state. An address pair can therefore describe the path currently used for packet delivery without serving as the sole identifier of the QUIC connection.

## QUIC Packets and Connection Identifiers

This subsection introduces the QUIC packet fields most relevant to connection continuity. Section 4 discusses the full migration behavior in more detail. Here, the purpose is to explain how QUIC packets can carry explicit connection identifiers rather than depending only on the address pair.

QUIC packets carry information that allows endpoints to associate packets with a connection. The most important field for this thesis is the connection identifier. A QUIC packet may carry a destination connection identifier and a source connection identifier [@rfc9000]. These identifiers allow an endpoint to associate an arriving packet with existing connection state without relying only on the source and destination IP addresses and port numbers. Figure \ref{fig:quic-packet} shows a simplified QUIC packet structure.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{packet.png}
\captionof{figure}{Simplified QUIC packet structure. Adapted from F5~\cite{f5_quic_http3}.}
\label{fig:quic-packet}
\end{center}

The destination connection identifier allows the receiving endpoint to identify the relevant connection state. The source connection identifier provides an identifier that the peer can use in the opposite direction. QUIC can also issue new connection identifiers during a connection. This allows an endpoint to change the identifier used on future packets, for example for routing or privacy reasons [@rfc9000].

TCP and QUIC differ in how this connection state is identified. A TCP connection is identified through the four-tuple of source address, source port, destination address, and destination port. QUIC still relies on addresses and ports for packet delivery, but its connection identifier provides another means to associate a packet with an existing connection. A change in the network path does not by itself change the identity of the QUIC connection.

A QUIC connection and the path currently carrying its packets can change independently. The connection represents transport and cryptographic state shared by the endpoints, while a path is determined by the address pair and route used for packet delivery. When the address pair changes, QUIC can first associate packets with the existing connection and then determine whether the new path is suitable for continued communication. The validation of such a path is discussed in Section 4.

## Streams and Multiplexing

This subsection introduces QUIC streams. Streams are important for QUIC deployment and HTTP/3 performance, but they are not the main mechanism behind connection migration. They are included here to complete the protocol overview before the thesis turns to path management in Section 4.

QUIC differs from TCP in connection establishment, path management, and the structure of data delivery. TCP provides a single ordered byte stream per connection. QUIC provides multiple streams within a single connection, with separate ordering and flow control at the stream level [@rfc9000].

The stream abstraction is significant for HTTP/3, as independent request-response exchanges can be placed on separate streams rather than serialized through a single transport-level byte stream. Packet loss may still affect congestion control and retransmission behavior at the connection level, but loss affecting one stream need not block data delivery on other streams in the same manner as in TCP-based transport. Stream multiplexing is a major source of the improved application behavior associated with QUIC-based transport [@rfc9000].

Within the scope of this thesis, streams are not the primary focus. Stream multiplexing is central to QUIC performance and to the design of HTTP/3, but the questions of mobility and multihoming depend more directly on how QUIC identifies and maintains connections across changing network paths.
