
In QUIC, connection migration refers to continuation of an existing connection over a new network path. In the classic TCP model, a change in the address pair generally causes transport failure, since connection identity is derived directly from source and destination addresses together with port numbers. QUIC departs from that model by allowing connection state to remain associated with an explicit connection identifier rather than solely with the current address pair [@rfc9000].

This design changes the transport response to address change. A new source or destination address does not by itself define a new connection. Instead, QUIC treats address change as an event that requires path assessment and protocol action [@rfc9000]. Hence, migration is not an optional add-on to QUIC, but part of its transport architecture.

Migration support rests on several related mechanisms. Connection identifiers preserve connection continuity across path change. Path validation tests whether a new path is suitable for communication. Congestion control and loss recovery adapt transport behavior after the path change [@rfc9000; @rfc9002]. Section 4 examines those mechanisms in turn.

## Connection Identifiers and Connection Continuity

The mechanism most closely tied to migration is the connection identifier. In classical TCP communication, packets are associated with connection state through the source and destination addresses together with their port numbers. In QUIC, by contrast, packets may be associated with connection state through an explicit connection identifier carried in the packet header [@rfc9000].

Since the connection identifier is independent of the current network-layer address pair, a QUIC connection does not depend exclusively on continued use of one address pair. A host may send from a new IP address, yet the peer may still associate incoming packets with existing transport state. Hence, QUIC separates connection continuity from path continuity in a way that TCP does not.

This distinction is central to the present thesis. In the traditional model, a change in address threatens the existence of the connection itself, since transport identity is derived from address information. In QUIC, the connection can remain the same even when the path changes, provided that the new path satisfies the protocol requirements [@rfc9000].

Connection identifiers also matter in deployment environments that include intermediaries. A server or load-balanced system may need a stable way to associate packets with existing state after an address change. Since the identifier need not change with the path, QUIC provides that stability at the transport layer [@rfc9000].

## Path Validation

Connection continuity alone is not sufficient for safe migration. A packet from a new address may reflect genuine host mobility, Network Address Translation (NAT) rebinding, or local path change. The same packet could also reflect spoofed traffic or an unsuitable route. RFC 9000 therefore defines an explicit path-validation procedure [@rfc9000].

Path validation serves two purposes. First, it allows an endpoint to determine whether the peer can receive traffic on the candidate path and can return traffic on that path. Second, it protects the protocol against incorrect migration decisions and certain spoofing attacks. Since address change cannot be trusted on observation alone, the protocol requires confirmation through a dedicated exchange [@rfc9000].

To test a path, an endpoint sends a `PATH_CHALLENGE` frame on the candidate path. The frame carries unpredictable data. RFC 9000 requires unpredictable content for each challenge, so that the sender can relate a response to a specific probe [@rfc9000]. The peer replies with a `PATH_RESPONSE` frame that echoes the received data. Validation succeeds only when the sender receives a matching response to a previously transmitted challenge.

An acknowledgment for a packet that carries a `PATH_CHALLENGE` frame does not count as proof of path validity. RFC 9000 makes that point explicitly, since an acknowledgment alone could be spoofed. The protocol accepts only the challenge-response exchange as proof that the peer can receive and return traffic on the tested path [@rfc9000]. Hence, path validation depends on more than simple packet receipt.

The exchange also has directional significance. A `PATH_RESPONSE` frame must be sent on the path where the `PATH_CHALLENGE` frame arrived [@rfc9000]. This rule gives the initiating endpoint evidence that the candidate path works in both directions. At the same time, the initiating endpoint must avoid assumptions that are too rigid about return-path symmetry, since migration scenarios may involve asymmetric conditions.

Path validation also interacts with datagram size requirements. RFC 9000 states that endpoints must expand datagrams that carry `PATH_CHALLENGE` and `PATH_RESPONSE` frames to at least 1200 bytes, unless anti-amplification limits prevent that action [@rfc9000]. The purpose of that requirement is not merely formal. A successful exchange with a datagram of that size shows not only that the peer address is reachable, but also that the path can carry QUIC-sized packets. If validation succeeds with a smaller datagram under anti-amplification limits, the peer address may be validated, but the path Maximum Transmission Unit has not yet been confirmed [@rfc9000].

The standard also allows repeated probes in the presence of loss. An endpoint may send more than one `PATH_CHALLENGE` frame if necessary, although the standard advises against placement of multiple challenges in the same packet [@rfc9000]. A path-validation attempt should also end on the basis of a timer rather than immediate failure after loss of a single probe. RFC 9000 recommends a timeout of three times the larger of the current Probe Timeout or the Probe Timeout estimated for the candidate path [@rfc9000]. Since a new path may differ substantially from the previous path in delay and loss behavior, a single lost challenge or response does not justify immediate rejection.

From an architectural perspective, path validation is one of the core mechanisms that enables migration in QUIC. Connection identifiers allow packets from a new path to remain associated with an existing connection. Path validation determines whether the new path is suitable for sustained use. Hence, migration support depends on both address-independent connection identification and explicit validation of the new path. Neither mechanism alone is sufficient [@rfc9000].

## Migration Triggers and Endpoint Response

Migration may follow several different events. One possibility is host mobility, where a device moves from one access network to another and receives a new IP address. Another possibility is NAT rebinding, where the externally visible address or port changes even though the host itself does not move. A third possibility is local path selection by a multihomed endpoint that chooses a different interface for policy or performance reasons [@rfc9000].

From the viewpoint of QUIC, those cases share a common feature. The peer observes packets from a new address pair. The protocol does not first classify the external cause and only then react. The protocol first detects the new path, then validates it, and only after that continues communication on the path if the validation succeeds [@rfc9000].

Base QUIC addresses migration between paths, not general concurrent use of multiple paths for ordinary data transfer. Hence, the base protocol addresses continuity across path change more directly than simultaneous exploitation of path diversity. That distinction is important for the present thesis, since mobility and multihoming overlap conceptually but do not imply identical transport behavior.

## Congestion Control and Loss Recovery on a New Path

A new path may differ from the previous path in delay, bandwidth, loss rate, and reordering behavior. Migration therefore affects not only address handling, but also transport dynamics. RFC 9002 treats congestion control and loss recovery as important parts of path change handling [@rfc9002].

The congestion controller in QUIC is path-specific. RTT estimation is also path-specific, and recovery behavior must adapt when communication moves to a new path [@rfc9002]. Since the new path may have substantially different characteristics, QUIC cannot safely assume that congestion state learned on the previous path remains valid without adjustment.

That point matters for interpretation of migration behavior. Successful path validation does not guarantee unchanged transport performance. A connection may remain alive after migration, yet throughput, latency, and loss behavior may differ noticeably from those observed before the path change. Hence, migration support preserves continuity, but continuity does not imply unchanged transport characteristics.

## NAT Rebinding and Operational Considerations

One practical motivation for migration support is that not every path change reflects host mobility in the ordinary sense. NAT devices may change the externally visible address or port used by a flow. In an address-bound transport protocol, that change may appear to represent a different endpoint. In QUIC, by contrast, the connection identifier allows packets to remain associated with existing state, while path validation allows the apparent new path to be tested before continued use [@rfc9000].

This behavior is particularly relevant in consumer and mobile networks, where address and port mappings may change independently of application behavior. QUIC thus improves robustness not only in explicit mobility cases, but also in environments where network devices alter the apparent path in ways that are invisible to the application.

At the same time, migration support introduces operational requirements. Endpoints must manage connection identifiers carefully, validate candidate paths before full use, and avoid policies that would expose unnecessary attack surface. Hence, migration in QUIC is both a protocol capability and an implementation concern.

## Load Balancers and Deployment Constraints

Migration has implications for load-balanced deployments as well. In a large-scale server system, packets for the same connection may need to reach a backend instance that holds the relevant transport state. If packets arrive from a different address pair after migration, the deployment still requires a way to route them consistently to the correct connection context. Connection identifiers support that requirement, since routing decisions need not depend solely on the current address pair [@rfc9000].

The protocol alone does not remove every deployment difficulty. Load balancers, stateless routing components, and backend connection management must remain compatible with the way connection identifiers are issued and interpreted. Hence, migration support in QUIC is not only a protocol property but also a deployment concern. The protocol makes migration possible, but infrastructure design still influences whether migration proceeds smoothly in practice.

## Multipath Extensions

Base QUIC supports migration between paths, but it does not define general concurrent use of multiple paths for ordinary data transfer within one connection. In that sense, base QUIC addresses continuity across path change more directly than simultaneous exploitation of path diversity [@rfc9000].

Multipath extensions extend the model by allowing one connection to use multiple paths concurrently. Such extensions are relevant to multihoming, since a multihomed endpoint may have several usable interfaces at the same time. Concurrent path use may improve robustness, aggregate capacity, or support policy-based traffic distribution. At the same time, the extension introduces additional complexity in scheduling, congestion control, failure handling, and path coordination.

For the purposes of the present thesis, the distinction between migration and multipath must remain clear. Migration concerns continuation of one connection across path change. Multipath concerns simultaneous use of multiple paths within one connection. The base QUIC specification addresses the first problem explicitly [@rfc9000]. The second problem lies beyond the scope of the base protocol and belongs to extension work.

## Summary

QUIC connection migration rests on the separation between connection identity and the current address pair. Connection identifiers allow packets from a new address to remain associated with existing transport state. Path validation determines whether the new path is suitable for sustained use. Congestion control and loss recovery then adapt transport behavior to the characteristics of that path [@rfc9000; @rfc9002].

From an architectural perspective, these mechanisms revise the transport response to address change. In address-bound transport protocols, a new address threatens the existence of the connection itself. In QUIC, a new address triggers procedures for validation and adaptation within an existing connection context. Hence, migration support in QUIC reflects a broader separation between connection identity and network location. The next section evaluates that behavior in a set of controlled scenarios.
