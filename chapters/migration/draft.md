Connection migration in QUIC refers to the continuation of an existing connection over a new network path. In the classic TCP model, a change in the address pair usually causes transport failure, since connection identity is derived from source and destination addresses together with port numbers. QUIC changes this model by allowing connection state to remain associated with an explicit connection identifier instead of only the current address pair [@rfc9000].

This section explains the protocol sequence that follows after an established QUIC connection observes an address change. Section 3 introduced connection identifiers as the basis for address-independent connection identification. However, connection identifiers alone do not explain how migration proceeds. This section therefore focuses on how QUIC decides whether packets from a new path should be used for continued communication. A packet from a new address pair may still belong to the existing connection, but the new path must be assessed before it can be trusted for sustained use.

Connection migration depends on four related mechanisms. First, connection identifiers preserve the association between arriving packets and connection state. Second, path validation tests whether the candidate path can carry traffic to and from the peer. Third, endpoint migration policy determines how the connection responds to the path change. Finally, congestion control and loss recovery adapt transmission behavior to the characteristics of the new path. Unless otherwise stated, the description in this section is based on RFC 9000 [@rfc9000]. Congestion-control behavior is based on RFC 9002 [@rfc9002].

## Migration Based on Connection Identifiers

Connection identifiers provide the first step in migration. When a peer receives a packet from a new address pair, the destination connection identifier allows the packet to be mapped to an existing QUIC connection. Therefore, the packet is processed within the existing connection context rather than treated immediately as the start of a new connection.

This first step is necessary because several events can change the observed path. The peer may have moved to another network, a NAT may have changed the externally visible address or port, or a multihomed endpoint may have selected another interface. These causes differ outside the protocol. However, they appear to QUIC in the same basic form: packets for an existing connection arrive from a different address pair.

The connection identifier resolves only the identity question. It tells the receiver that the packet can be associated with existing connection state. However, it does not prove that the new path is safe for continued traffic. A valid connection identifier could still arrive through a path that cannot carry return traffic, or through traffic that reflects spoofing or other unwanted behavior.

Hence, QUIC separates connection identification from path approval. Connection identifiers answer whether the packet belongs to an existing connection. Path validation answers whether the candidate path can safely carry further traffic for that connection. Migration requires both steps.

A simplified migration sequence is shown in Figure \ref{fig:migration-sequence}.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{mermaid.png}
\captionof{figure}{Simplified QUIC migration sequence.}
\label{fig:migration-sequence}
\end{center}

## Path Validation

Path validation follows from the limitation of connection identifiers. Once a packet has been associated with an existing connection, the endpoint still needs evidence that the new path can support communication. A new address may represent genuine host mobility, NAT rebinding, or local path selection by a multihomed endpoint. However, the same observation may also result from spoofed traffic or from a path that cannot carry return traffic.

QUIC validates a candidate path through a challenge-response exchange. The validating endpoint sends a `PATH_CHALLENGE` frame on the candidate path. The frame contains unpredictable data. The peer replies with a `PATH_RESPONSE` frame that echoes the same data. Validation succeeds only when the endpoint receives a response that matches a challenge it previously sent.

This exchange proves more than receipt of an arbitrary packet. An acknowledgment for a packet carrying `PATH_CHALLENGE` is not enough, since an acknowledgment does not prove that the peer returned the challenge data on the tested path. Instead, the matching `PATH_RESPONSE` shows that the peer received the challenge and could send the required response from the candidate path.

The return path also matters. A `PATH_RESPONSE` frame must be sent on the path where the corresponding `PATH_CHALLENGE` frame arrived. Therefore, the response is tied to the candidate path itself. This rule gives the initiating endpoint evidence that packets can travel in both directions on that path, not merely that the peer can acknowledge packets through some other route.

Path validation also checks whether the path can carry packets of a useful size. RFC 9000 requires datagrams that contain `PATH_CHALLENGE` or `PATH_RESPONSE` frames to be expanded to at least 1200 bytes unless anti-amplification limits prevent it. This size is important because QUIC endpoints must be able to send UDP datagrams of at least 1200 bytes during normal operation. Hence, a successful exchange with such a datagram shows that the peer address is reachable and that the path can carry the minimum datagram size expected by QUIC. If validation succeeds only with a smaller datagram under anti-amplification limits, the peer address may be validated, but the path has not yet shown that it can carry normal QUIC datagrams.

The procedure also accounts for packet loss. A single missing `PATH_RESPONSE` does not necessarily mean that the path is unusable. The candidate path may have different delay, loss, or reordering behavior from the old path. Therefore, a path-validation attempt should end on the basis of a timer rather than the loss of one probe. Repeated `PATH_CHALLENGE` frames may also be sent when necessary.

Path validation completes the safety step that connection identifiers cannot provide. Connection identifiers preserve the connection context across address change. Path validation tests whether the new path can support continued communication. Together, these mechanisms allow migration to proceed without treating every address change as either a new connection or an immediately trusted path.

## Migration Triggers and Endpoint Response

Migration may follow several different events. One case is host mobility, where a device moves from one access network to another and receives a new IP address. Another case is NAT rebinding, where the externally visible address or port changes even though the host itself does not move. A third case is local path selection, where a multihomed endpoint selects another interface for policy or performance reasons.

From the QUIC perspective, these cases share the same protocol-level symptom. Packets for an existing connection arrive from a new address pair. Therefore, QUIC does not need to classify the external cause before it reacts. The protocol first uses the connection identifier to associate the packet with existing connection state. It then treats the new address pair as a candidate path that may require validation.

This response separates the protocol mechanism from the external reason for address change. Mobility, NAT rebinding, and local interface selection may arise from different network conditions. However, each case follows the same protocol sequence: detect the new path, associate the packet with the existing connection, validate the path if required, and continue communication only when the path is acceptable.

This sequence also clarifies the scope of base QUIC. Base QUIC supports continuation across a path change, so it directly addresses migration. It does not define ordinary data transfer over several paths at the same time. Therefore, base QUIC treats mobility more directly than full multipath communication, even though mobility and multihoming are related at the architectural level.

## Congestion Control and Loss Recovery on a New Path

Migration affects more than address handling. A new path may differ from the previous path in round-trip time, bandwidth, loss rate, and packet reordering. Therefore, congestion-control state learned on the old path may not describe the new path. QUIC loss recovery and congestion control treat these values as path-specific concerns [@rfc9002].

When communication moves to a new path, the sender cannot safely reuse all congestion-control information from the previous path. A congestion window that was appropriate for the old path may overload the new path. An old round-trip-time estimate may also lead to incorrect loss detection or retransmission timing. Hence, the sender must adapt its congestion-control and recovery behavior to the candidate path.

In practical terms, the connection continues but the path-specific transport state must be established for the new path. The endpoint must learn the delay, loss behavior, and available capacity of that path from packets sent on it. This distinction is important: migration preserves the QUIC connection, but it does not preserve all performance assumptions from the old path.

This distinction also matters for the interpretation of migration results. Successful migration means that the connection survives the address change. It does not mean that throughput, latency, or loss behavior remain unchanged. A migrated connection may experience temporary disruption while the new path is validated and while congestion control adapts to the new path. Therefore, connection continuity and performance continuity are related but separate properties.

## NAT Rebinding and Operational Considerations

Not every path change reflects visible host mobility. NAT devices may change the externally visible address or port used by a flow. In an address-bound transport protocol, this change may appear to represent a different endpoint. In QUIC, the connection identifier allows packets from the new address pair to remain associated with existing connection state.

NAT rebinding is therefore one practical reason for migration support in QUIC. It may occur without application-level action and without explicit movement by the host. From the application perspective, communication may appear continuous. From the transport perspective, the peer address has changed and the apparent path may require validation.

This case shows why migration support is useful beyond obvious mobility scenarios. Address and port mappings may change independently of application behavior, especially in consumer and mobile networks. QUIC improves robustness in such environments because the visible address change does not automatically destroy the connection context.

However, this robustness also creates implementation responsibilities. Endpoints must manage connection identifiers carefully, validate candidate paths before full use, and avoid policies that expose unnecessary attack surface. Hence, migration in QUIC is both a protocol capability and an implementation concern.

## Load Balancers and Deployment Constraints

Migration also affects load-balanced deployments. In a large server deployment, packets for one QUIC connection may need to reach the backend instance that holds the relevant connection state. If packets arrive from a new address pair after migration, address-based routing alone may no longer send them to the correct backend.

Connection identifiers help with this deployment problem. A load balancer can use information in the connection identifier to route packets to the backend associated with the connection. Therefore, routing does not need to depend solely on the current address pair. This allows a connection to survive path change without losing access to the server-side state.

However, this benefit depends on deployment design. Load balancers, stateless routing components, and backend systems must interpret connection identifiers consistently. Connection identifiers must also be issued and managed in a way that supports routing, privacy, and operational policy.

Thus, migration support is not only a protocol property. QUIC makes migration possible at the transport layer, but infrastructure design determines whether packets after migration still reach the correct connection context. Deployment architecture therefore influences whether migration proceeds smoothly in practice.

## Multipath Extensions

Base QUIC supports migration between paths. In this model, the connection moves from one path to another after a path change or path selection event. Base QUIC does not define general concurrent use of multiple paths for ordinary data transfer within one connection.

This distinction matters for multihoming. A multihomed endpoint may have several usable interfaces at the same time, but base QUIC does not use them as simultaneous data paths by default. Instead, it provides mechanisms that allow the connection to continue when the active path changes. Therefore, base QUIC addresses continuity across path change more directly than simultaneous exploitation of path diversity.

Multipath extensions extend this model by allowing one QUIC connection to use multiple paths at the same time. Concurrent path use may improve robustness, aggregate capacity, or policy-based traffic distribution. However, it also introduces additional complexity in scheduling, congestion control, failure handling, and packet reordering across paths.

For the purposes of this thesis, the distinction between migration and multipath remains important. Migration concerns continuation of one connection across path change. Multipath concerns simultaneous use of multiple paths within one connection. Since base QUIC validates and switches between paths rather than using several paths at the same time, it specifies migration behavior but leaves general multipath communication to extension work.

## Summary

QUIC connection migration depends on a sequence of related mechanisms. Connection identifiers allow packets from a new address pair to remain associated with existing connection state. Path validation checks whether the new path can support communication. Congestion control and loss recovery adapt transmission behavior to the characteristics of that path.

Together, these mechanisms revise the transport response to address change. In address-bound transport protocols, a new address threatens the existence of the connection itself. In QUIC, a new address triggers validation and adaptation within an existing connection context. The connection can remain the same while the path changes.

However, migration support is not equivalent to complete mobility or full multipath communication. Successful migration still depends on validation, path-specific transport behavior, endpoint policy, and deployment infrastructure. Therefore, QUIC provides transport-level continuity across path change, while broader multipath use and deployment behavior remain separate concerns. The next section evaluates that behavior in controlled scenarios.
