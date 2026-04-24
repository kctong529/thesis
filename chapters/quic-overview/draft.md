
QUIC is the transport protocol examined in the remainder of this thesis. HTTP and HTTP/3 are introduced here only as the deployment context that motivated QUIC development. After that, the section focuses on QUIC itself: its UDP-based deployment model, secure transport design, connection identifiers, packet structure, and stream abstraction.

## Evolution of HTTP as Motivation for QUIC

Transport protocols provide mechanisms such as reliability, congestion control, and ordered delivery. They do not define the meaning of the data exchanged between applications. Application-layer protocols specify the structure of messages, the interpretation of requests and responses, and the semantics assigned to exchanged data [@kurose2025].

In Internet applications, this role is often performed by the hypertext transfer protocol (HTTP). HTTP defines a request-response model in which a client sends a request and a server returns a response with status information, metadata, and, when appropriate, a representation of the requested resource [@rfc9110]. HTTP provides the semantic structure for many application-layer exchanges, while the transport protocol carries the data between endpoints [@kurose2025].

Early versions of HTTP were developed for a web environment with relatively simple pages and a limited number of associated resources. As web applications became more interactive and media-rich, the number of concurrent resource transfers increased. Modern web pages often require scripts, style sheets, images, fonts, and asynchronous application data. This communication pattern placed increasing pressure on the transport layer [@kurose2025].

HTTP/1.1 improved performance through persistent connections, but browsers still commonly opened multiple parallel TCP connections to the same origin. HTTP/2 introduced multiplexing over a single TCP connection, but it still inherited the ordered byte-stream semantics of TCP. Therefore, packet loss at the TCP layer could delay otherwise independent application data. QUIC was developed in response to these transport limitations, and HTTP/3 was later defined as HTTP over QUIC [@kurose2025; @rfc9000].

For the purposes of this thesis, HTTP/3 is mainly relevant as a deployment driver for QUIC. The rest of the thesis does not analyze HTTP semantics. Instead, it focuses on QUIC as a transport protocol that separates connection identity from the current address pair.

## QUIC as a UDP-based Secure Transport

QUIC differs from TCP not only in its protocol mechanisms, but also in its deployment model. It runs above UDP while providing many functions normally associated with TCP. This placement gives QUIC a different deployment path from TCP while preserving reliable and secure transport semantics.

QUIC is a general-purpose transport protocol standardized by the Internet Engineering Task Force (IETF) in RFC 9000 [@rfc9000]. One major difference between QUIC and TCP is that QUIC operates over the user datagram protocol (UDP). UDP is a minimal transport protocol that provides port-based delivery between applications, but it does not by itself provide connection establishment, reliability, retransmission, congestion control, stream abstraction, or ordered delivery. In the traditional Internet stack, these functions are typically associated with TCP rather than UDP [@kurose2025].

The use of UDP allows QUIC to implement transport functionality in user space rather than in operating system kernels. User-space deployment avoids the need to introduce new transport behavior directly into kernel TCP implementations and allows protocol evolution to proceed more rapidly [@rfc9000]. QUIC uses UDP as a substrate, while the more complex transport functions are implemented within the QUIC protocol itself.

The use of UDP does not imply that QUIC provides only an unreliable datagram service. QUIC implements reliability, acknowledgments, retransmission behavior, congestion control, flow control, packet numbering, and ordered delivery within the protocol itself [@rfc9000; @rfc9002]. QUIC retains many transport functions traditionally associated with TCP, but it changes the context in which those functions are implemented and deployed.

Security is also part of the QUIC transport design. QUIC incorporates TLS 1.3 into connection establishment instead of placing encryption in a separate layer above transport [@rfc9000]. During the handshake, the endpoints establish cryptographic keys and negotiate transport parameters. After the handshake, most QUIC packet contents are protected, while the packet header still carries the information needed for routing and connection identification. This integration means that QUIC connection state includes both transport state and cryptographic state.

A simplified view of the protocol stack is shown in Figure \ref{fig:quic-stack}.

\begin{center}
\includegraphics[width=0.3\linewidth,keepaspectratio]{stack.png}
\captionof{figure}{QUIC protocol stack}
\label{fig:quic-stack}
\end{center}

This stack position is important for the thesis. QUIC remains compatible with the deployed Internet through UDP, but it defines its own connection state and connection identifiers above UDP. This design creates the basis for connection continuity across path changes.

## QUIC Packets and Connection Identifiers

This subsection introduces the QUIC packet fields most relevant to connection continuity. Section 4 discusses the full migration behavior in more detail. Here, the purpose is to explain how QUIC packets can carry explicit connection identifiers rather than depending only on the address pair.

QUIC packets carry information that allows endpoints to associate packets with a connection. The most important field for this thesis is the connection identifier. A QUIC packet may carry a destination connection identifier and a source connection identifier [@rfc9000]. These identifiers allow an endpoint to associate an arriving packet with existing connection state without relying only on the source and destination IP addresses and port numbers.

A simplified QUIC packet structure is shown in Figure \ref{fig:quic-packet}.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{packet.png}
\captionof{figure}{Simplified QUIC packet structure. Adapted from F5~\cite{f5_quic_http3}.}
\label{fig:quic-packet}
\end{center}

The destination connection identifier identifies the connection state at the receiving endpoint. The source connection identifier provides an identifier that the peer can use in the opposite direction. QUIC can also issue new connection identifiers during a connection. This allows an endpoint to change the identifier used on future packets, for example for routing or privacy reasons [@rfc9000].

The connection identifier is the key difference from the classical TCP model. In TCP, the four-tuple of source address, source port, destination address, and destination port identifies the connection. In QUIC, the address pair still matters for packet delivery, but it is not the only basis for connection identification. This separation allows QUIC to maintain connection state even when the network path changes.

The distinction between connection and path is central to later migration behavior. A QUIC connection refers to the transport state shared by the endpoints. A path refers to the address pair and route currently used to carry packets. Section 4 explains how QUIC validates a new path and decides whether the connection can continue over that path.

## Streams and Multiplexing

This subsection introduces QUIC streams. Streams are important for QUIC deployment and HTTP/3 performance, but they are not the main mechanism behind connection migration. They are included here to complete the protocol overview before the thesis turns to path management in Section 4.

QUIC differs from TCP in connection establishment, path management, and the structure of data delivery. TCP provides a single ordered byte stream per connection. QUIC provides multiple streams within a single connection, with separate ordering and flow control at the stream level [@rfc9000].

The stream abstraction is significant for HTTP/3, as independent request-response exchanges can be placed on separate streams rather than serialized through a single transport-level byte stream. Packet loss may still affect congestion control and retransmission behavior at the connection level, but loss affecting one stream need not block data delivery on other streams in the same manner as in TCP-based transport. Stream multiplexing is a major source of the improved application behavior associated with QUIC-based transport [@rfc9000].

Within the scope of this thesis, streams are not the primary focus. Stream multiplexing is central to QUIC performance and to the design of HTTP/3, but the questions of mobility and multihoming depend more directly on how QUIC identifies and maintains connections across changing network paths.
