
Connection migration in QUIC refers to the continuation of an existing connection over a new network path. In the classic TCP model, a change in the address pair usually causes transport failure, since connection identity is derived from source and destination addresses together with port numbers. QUIC changes this model by allowing connection state to remain associated with an explicit connection identifier instead of only the current address pair [@rfc9000].

This section explains the protocol sequence that follows after an established QUIC connection observes an address change. Section 3 introduced connection identifiers as the basis for address-independent connection identification. However, connection identifiers alone do not explain how migration proceeds. For this reason, this section focuses on how QUIC decides whether packets from a new path should be used for continued communication. A packet from a new address pair may still belong to the existing connection, but the new path must be assessed before it can be trusted for sustained use.

Connection migration depends on four related mechanisms. First, connection identifiers preserve the association between arriving packets and connection state. Second, path validation tests whether the candidate path can carry traffic to and from the peer. Third, endpoint migration policy determines how the connection responds to the path change. Finally, congestion control and loss recovery adapt transmission behavior to the characteristics of the new path. Unless otherwise stated, the description in this section is based on RFC 9000 [@rfc9000]. Congestion-control behavior is based on RFC 9002 [@rfc9002].

## Migration Based on Connection Identifiers

Connection identifiers provide the first step in migration. When a peer receives a packet from a new address pair, the destination connection identifier allows the packet to be mapped to an existing QUIC connection. Therefore, the packet is processed within the existing connection context rather than treated immediately as the start of a new connection.

This first step is necessary because several events can change the observed path. The peer may have moved to another network, a NAT may have changed the externally visible address or port through NAT rebinding, or a multihomed endpoint may have selected another interface. NAT rebinding occurs when a middlebox, usually a NAT, assigns a new external port or IP address to an existing flow [@rfc9000]. These causes differ outside the protocol. However, they appear to QUIC in the same basic form: packets for an existing connection arrive from a different address pair.

The connection identifier resolves only the question of connection identity. It tells the receiver that the packet can be associated with existing connection state. However, it does not prove that the new path is safe for continued traffic. A valid connection identifier could still arrive through a path that cannot carry return traffic, or through traffic that reflects spoofing or other unwanted behavior.

Hence, QUIC separates connection identification from path approval. Connection identifiers answer whether the packet belongs to an existing connection. Path validation answers whether the candidate path can safely carry further traffic for that connection. Migration requires both steps. A simplified migration sequence is shown in Figure \ref{fig:migration-sequence}.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{mermaid.png}
\captionof{figure}{Simplified QUIC migration sequence.}
\label{fig:migration-sequence}
\end{center}

## Path Validation

Path validation follows from the limitation of connection identifiers. Once a packet has been associated with an existing connection, the endpoint still needs evidence that the new path can support communication. A new address may represent genuine host mobility, NAT rebinding, or local path selection by a multihomed endpoint. However, the same observation may also result from spoofed traffic or from a path that cannot carry return traffic.

QUIC validates a candidate path through a challenge-response exchange. The validating endpoint sends a `PATH_CHALLENGE` frame on the candidate path. The frame contains unpredictable data. The peer replies with a `PATH_RESPONSE` frame that echoes the same data. Validation succeeds only when the endpoint receives a response that matches a challenge it previously sent.

This exchange proves more than receipt of an arbitrary packet. An acknowledgment for a packet carrying `PATH_CHALLENGE` is not enough, since an acknowledgment does not prove that the peer returned the challenge data on the tested path. Instead, the matching `PATH_RESPONSE` shows that the peer received the challenge and could send the required response from the candidate path.

The return path also matters. A `PATH_RESPONSE` frame must be sent on the path where the corresponding `PATH_CHALLENGE` frame arrived. The peer must return the response through the candidate path. A matching response from that path provides evidence that the tested address pair supports communication in both directions.

The validation exchange also tests the datagram size supported by the candidate path. RFC 9000 requires datagrams that contain `PATH_CHALLENGE` or `PATH_RESPONSE` frames to reach at least 1200 bytes unless the anti-amplification limit prevents this [@rfc9000]. Before validation of a peer address, QUIC restricts the amount of data that an endpoint may send to that address relative to the amount already received. The restriction prevents a spoofed source address from directing a much larger amount of traffic toward another host. A successful exchange with 1200-byte datagrams also establishes that the path supports the minimum datagram size required by QUIC. If the anti-amplification limit permits only a smaller datagram, the exchange may validate the peer address, but a later validation must still establish support for the required path MTU.

The procedure also accounts for packet loss. A single missing `PATH_RESPONSE` does not necessarily mean that the path is unusable. The candidate path may have different delay, loss, or reordering behavior from the old path. Therefore, a path-validation attempt should end on the basis of a timer rather than the loss of one probe. Repeated `PATH_CHALLENGE` frames may also be sent when necessary.

Path validation completes the safety step that connection identifiers cannot provide. Connection identifiers preserve the connection context across address change. Path validation tests whether the new path can support continued communication. Together, these mechanisms allow migration to proceed without treating every address change as either a new connection or an immediately trusted path.

## Migration Procedure and Endpoint Response

RFC 9000 allows an endpoint to test a new local address before it moves the connection to that address. `PATH_CHALLENGE`, `PATH_RESPONSE`, `NEW_CONNECTION_ID`, and `PADDING` are probing frames. A packet that contains only these frames is a probing packet, while a packet that contains another frame type is a non-probing packet [@rfc9000].

A probe can establish reachability without moving ordinary traffic to the candidate path. The endpoint initiates migration when it sends a non-probing packet from a new local address. At the other endpoint, receipt of a non-probing packet from a new peer address indicates that the peer has migrated to that address [@rfc9000].

If the peer permits the migration, it sends later packets to the new address and starts path validation if no validation is already in progress. RFC 9000 uses the packet number to protect this decision against packet reordering. The peer address used for transmission changes only in response to the highest-numbered non-probing packet. A delayed packet from an older path cannot by itself restore that old address as the active peer address.

Host mobility, NAT rebinding, and local interface selection can all produce this protocol sequence. A device may acquire a new address on another network. A NAT may replace the externally visible address or port without any action by the application. A multihomed endpoint may also select another interface. QUIC can react to the new peer address without first determining which of these events caused it.

QUIC version 1 restricts normal connection migration to new client addresses, and the client initiates such migration [@rfc9000]. A peer can also advertise the `disable_active_migration` transport parameter during connection establishment. The parameter prevents active migration to another local address for communication with the peer address used during the handshake. Section 4.6 describes the separate mechanism through which a server can provide another address for the connection.

Base QUIC moves an existing connection from one active path to another. It does not define ordinary application-data transfer over several active paths at the same time.

## Congestion Control and Loss Recovery on a New Path

Packets sent on the old path must not contribute to congestion control or round-trip-time estimation for the new path [@rfc9000]. After confirmation that the peer owns the new address, the endpoint resets the congestion controller and RTT estimator for that path to their initial values. RFC 9000 makes an exception when only the peer UDP port changes.

The new path may have a different capacity, round-trip time, loss rate, or degree of packet reordering. A congestion window that suited the previous path may exceed the capacity available on the new one. An RTT estimate from the old path can also produce unsuitable loss-detection or retransmission timing.

The endpoint validates explicit congestion notification (ECN) capability again on the new path [@rfc9000]. ECN allows network devices to indicate congestion without packet loss. Support can differ between paths, so ECN state from the old path does not automatically apply after migration.

The QUIC connection remains intact while the endpoint establishes new path-specific transport state. Streams and cryptographic state do not have to be recreated merely because the congestion controller and RTT estimator start again. Throughput and delay can still change after a successful migration, particularly during path validation and the initial adaptation to the new path.

## Security and Privacy During Migration

A packet can belong to an established QUIC connection without proving that its source address belongs to the peer. A malicious peer could present the address of another host and cause the endpoint to direct traffic toward that host. Path validation and the anti-amplification limit restrict how much traffic an endpoint can send before it has evidence that the peer can receive packets at the new address [@rfc9000].

RFC 9000 also considers a spurious migration caused by an attacker that copies a genuine packet and forwards it with a different source address. If the copied packet arrives first, the endpoint can initially interpret it as traffic from a new peer address. Failure of path validation causes the endpoint to return to the last validated peer address. A later packet with a higher packet number from the legitimate path can also cause the endpoint to move back to that path [@rfc9000].

NAT rebinding can produce a similar address change without an attack. A NAT may assign a new external port or IP address to an existing flow even though the host has not deliberately moved. RFC 9000 requires validation after a peer address change unless the endpoint has already validated that address [@rfc9000]. The connection identifier still allows packets from the new NAT mapping to reach the existing connection state.

Connection identifier reuse creates a separate privacy concern. A passive observer could correlate packets on two paths if the same connection identifier appeared on both. RFC 9000 requires an endpoint to avoid reuse of one connection identifier across different local addresses or different destination addresses [@rfc9000].

A change of connection identifier does not remove every means of correlation. Packet timing and packet size remain visible and can reveal similarities between traffic on different paths. The identifier itself no longer provides a direct link between them.

## Load Balancers and Deployment Constraints

Some server deployments choose a backend from the source and destination IP addresses and ports of an incoming packet. A client address change can alter that choice even though the QUIC connection has not changed. Later packets may reach a backend that has no state for the connection [@rfc9000].

RFC 9000 permits an out-of-band mechanism that forwards packets to the correct backend according to the connection identifier [@rfc9000]. The backend that owns the connection state can continue to receive the packets after the client address changes.

A server can also provide a `preferred_address` transport parameter during the handshake. The parameter contains an alternative IPv4 or IPv6 server address and connection information for later use [@rfc9000]. This mechanism suits deployments in which the client initially contacts an address shared by several servers but can later use an address associated more directly with the established connection.

The client validates the path to the preferred address before it moves the connection there. A successful validation allows later packets to use the preferred server address and an unused connection identifier. If validation fails, the client continues to use the original server address [@rfc9000].

A server that cannot preserve access to the correct connection state after a client address change can advertise `disable_active_migration` [@rfc9000]. The client then cannot use ordinary active migration with the original server address. The `preferred_address` mechanism remains available because the server supplies that address as part of the connection setup.

## Multipath Extensions

RFC 9000 permits probes on several candidate paths at the same time when the peer has supplied enough unused connection identifiers [@rfc9000]. Each new local address used for a probe requires a previously unused connection identifier. The available identifiers therefore limit the number of candidate paths that an endpoint can test concurrently.

Several active probes do not mean that application data uses several paths. Ordinary traffic can remain on the current path while the endpoint tests alternatives. A multihomed host with both Wi-Fi and cellular connectivity can, for example, test another path before it moves the connection.

Multipath extensions allow several paths to carry data for one QUIC connection at the same time. Such extensions need rules that select a path for each packet and maintain congestion state for the available paths. They also need to account for path failure and differences in packet arrival time.

Base QUIC therefore provides migration from one active path to another and permits concurrent tests of candidate paths. General concurrent data transfer across several paths belongs to multipath extensions.

## Summary

A destination connection identifier can associate a packet from a new address with an established QUIC connection. Path validation can then test the newly observed path without creation of another connection. Probe packets allow a path to be tested before a non-probing packet indicates that migration has occurred.

After migration, the endpoint establishes congestion-control, RTT, and ECN state for the new path. The connection itself can retain its streams, cryptographic context, and other connection state. Security rules limit traffic toward an unvalidated address, and connection identifier changes reduce direct correlation between traffic on different paths.

Server infrastructure must also preserve access to the backend that owns the connection state after a client address changes. Connection-ID-based forwarding and the server `preferred_address` mechanism provide two options described by RFC 9000. Base QUIC can test several candidate paths, but simultaneous application-data transfer over several paths requires multipath extensions.
