
In the early days of the Internet, connecting to a host essentially meant connecting to its IP address. That address was expected to remain the same throughout the lifetime of the connection. Most machines were stationary, and the IP address served both as a routing locator and as a stable identifier of the host. In that environment, binding a transport connection to a pair of IP addresses and port numbers worked well and rarely caused problems.

Today, that assumption no longer holds. Devices frequently switch networks while applications run in the background. From the application's perspective, nothing has changed: the session is still active. At the transport layer, though, a new IP address looks like a different endpoint, and the connection is dropped. This behavior reveals a deeper architectural coupling between session identity and network location.

## Identity and Location in Classical Transport

Internet communication requires continuity across multiple transmissions. To sustain such interaction, each host maintains state describing what has been sent, received, and acknowledged. The network layer itself does not maintain this state. Following the end-to-end principle [@saltzer1984end], reliability and ordering mechanisms reside at the endpoints, while the network provides only best-effort packet delivery.

Because the network does not track active sessions, the endpoints must determine how each incoming packet relates to stored communication state. In the classical Internet architecture, this association is derived from the source and destination IP addresses together with their port numbers. A transport connection is therefore identified by this four-tuple (sometimes informally referred to as the 5-tuple including protocol number). Session identity is implicitly bound to network location.

This binding between identity and location is not explicitly stated in early Internet specifications; rather, it emerges from how transport protocols were implemented. In TCP, for example, connection state is indexed by the combination of source and destination IP addresses and port numbers. As long as these values remain stable, the association between packets and session state is preserved. When they change, the transport layer treats subsequent packets as belonging to a different connection. The mechanism is simple and efficient, but it assumes stability in network attachment.

That assumption is increasingly misaligned with modern deployment environments. Hosts are often multihomed, maintaining multiple interfaces simultaneously. Address translation devices may rewrite source addresses and ports. Routing paths may change independently of application behavior. Under these conditions, the equivalence between "who is communicating" and "where the host is located" becomes fragile.

When a host's address changes, this binding breaks. The transport layer interprets the new address as a new endpoint. The previous session is lost, even though the communicating application has not intentionally terminated it.

A number of architectural approaches have attempted to address this tension at different layers of the stack. These include network-layer mechanisms that introduce indirection and transport-layer extensions that tolerate multiple addresses. However, such solutions have faced deployment and compatibility constraints in the open Internet.

## QUIC and Thesis Scope

QUIC challenges this assumption by introducing an explicit connection identifier carried within the protocol itself [@rfc9000]. Unlike the traditional four-tuple, this identifier is independent of IP addressing and can remain stable even as network-layer addresses change. Packets can therefore be associated with existing transport state despite changes in network attachment. This design shifts session identity from an implicit property of routing information to an explicit element of the transport protocol.

This thesis investigates how QUIC redefines transport-layer identity to accommodate mobility and multihoming. It examines the mechanisms that enable connection migration, analyzes their interaction with network devices such as NATs and load balancers, and evaluates the architectural implications of separating session identity from network location. By situating QUIC within the broader evolution of Internet transport design, the thesis aims to clarify both its contributions and its trade-offs.
