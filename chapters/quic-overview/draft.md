## HTTP/3 and QUIC Overview

### QUIC and HTTP/3 in the protocol stack

HTTP/3 is the first standardized version of HTTP that runs over QUIC rather than over TCP. In earlier protocol stacks, HTTP relied on TCP for reliable transport and on a separate security layer for encryption. In the HTTP/3 stack, QUIC provides transport services directly, including connection establishment, stream multiplexing, loss recovery, congestion control, and integrated cryptographic negotiation [@rfc9000].

For the purposes of the present thesis, the distinction between HTTP/3 and QUIC is important. HTTP/3 is an application protocol that maps HTTP semantics onto QUIC, whereas the mechanisms relevant to mobility and multihoming are properties of QUIC itself. The architectural focus of this section therefore remains on QUIC, while HTTP/3 is introduced mainly as the most prominent application protocol built on top of it.

### QUIC as a UDP-Based Transport Protocol

QUIC is defined as a UDP-based multiplexed and secure transport protocol [@rfc9000]. The use of UDP allows QUIC to be implemented in user space rather than in the operating system kernel. User-space deployment makes implementation updates and protocol evolution more practical than in the case of TCP, where transport behavior is traditionally embedded more deeply in the system software.

Running over UDP does not mean that QUIC provides only an unreliable datagram service. QUIC implements reliability, acknowledgments, retransmission behavior, congestion control, and ordered delivery within the protocol itself [@rfc9000; @rfc9002]. In that sense, QUIC retains many transport functions traditionally associated with TCP while changing the architectural context in which those functions are implemented.

### Security and Connection Establishment

A second major difference between QUIC and earlier transport designs is the integration of security into the transport protocol. QUIC incorporates cryptographic negotiation as part of connection establishment and does not treat encryption as an optional add-on layered above an otherwise complete transport service [@rfc9000].

This integration has two architectural consequences. First, transport establishment and cryptographic establishment are closely coupled. Second, encrypted transport becomes a normal property of the protocol rather than a separate deployment choice. In practical terms, QUIC reduces the separation between transport functionality and session protection that characterized the traditional TCP-based web stack.

### Streams and Multiplexing

QUIC differs from TCP not only in connection establishment but also in the structure of data delivery. TCP provides a single ordered byte stream per connection. QUIC, by contrast, provides multiple streams within a single connection, with separate ordering and flow control at the stream level [@rfc9000].

The stream abstraction is particularly important for HTTP/3, because independent request-response exchanges can be placed on separate streams rather than serialized through one transport-level byte stream. As a result, packet loss on one stream does not necessarily block data delivery on other streams in the same way as in TCP-based transport. Stream multiplexing is therefore one of the main reasons QUIC improves application behavior in comparison with earlier web transport designs [@rfc9000].

Within the scope of the present thesis, however, streams are not the main issue. Stream multiplexing is central to QUIC performance and to the design of HTTP/3, but the questions of mobility and multihoming depend more directly on how QUIC identifies and maintains connections across changing network paths.

### Connection Identifiers and Path Management

The feature of QUIC most directly relevant to mobility and multihoming is the separation between connection identity and the current address pair. In classical TCP communication, packets are associated with connection state through the source and destination addresses and port numbers. In QUIC, packets can instead be associated with connection state through an explicit connection identifier carried in the packet header [@rfc9000].

The connection identifier is independent of the currently used network-layer address pair. As a result, a QUIC connection does not become invalid merely because a host begins sending from a different IP address. RFC 9000 also defines path validation and migration-related behavior, which makes it possible to test a new path before using it for sustained communication [@rfc9000]. In architectural terms, QUIC distinguishes more clearly between an ongoing connection and the particular network path currently used to carry packets.

### Relevance to Mobility and Multihoming

The relevance of QUIC to the present thesis follows from the protocol’s treatment of connection continuity under address change. Mobility and multihoming are no longer immediate connection-breaking events in the same way as in the classical TCP model. Instead, address change becomes a transport event that QUIC can detect, validate, and potentially accommodate through explicit protocol mechanisms [@rfc9000].

The practical outcome still depends on factors such as path validation, congestion state, endpoint policy, and middlebox behavior. QUIC does not remove the operational complexity of mobility and multihoming, but it changes the architectural basis on which those problems are handled. Loss detection and congestion control remain important parts of that behavior, particularly when communication shifts onto a new path [@rfc9002].

For that reason, the following section examines QUIC connection migration in more detail. The main focus is on how QUIC validates new paths, manages connection state across address changes, and balances architectural flexibility against operational and deployment constraints.
