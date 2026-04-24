
The literature-based analysis in the previous sections explains how QUIC connection migration is intended to mitigate the identity-location problem at the transport layer. This section complements that analysis with a small-scale exploratory evaluation. The purpose of the evaluation is not to provide a general performance benchmark, but to observe how different transport approaches behave when the client path or address changes during an ongoing session.

## Experimental Setup

The experiments use a controlled Mininet topology to emulate a path change during an active client-server session. A client and server first communicate normally over one path. After the session has been established, a forced path or address change is introduced while communication is still active. This creates a repeatable mobility-like event in which the network attachment changes but the application-level communication goal remains the same.

Three cases are compared. The first case uses plain TCP, which has no built-in support for connection migration. The second case uses TCP with explicit reconnect, which acts as an application-level recovery baseline. In this case, the original TCP connection is not expected to survive the address change, but the application attempts to recover by opening a new connection. The third case uses QUIC, which supports built-in transport-layer migration through connection identifiers and path validation.

The goal is to observe how each approach behaves under the same network event rather than under unrelated network conditions. This makes it possible to distinguish between transport-level continuity and application-level recovery. Plain TCP represents the behavior of a traditional address-bound transport connection. TCP with reconnect represents the best-case recovery behavior available to an application that can detect failure and reconnect. QUIC represents a transport design in which the original connection may continue across the path change.

The comparison focuses on four criteria:

- whether continuity is preserved;
- how long communication takes to resume;
- how much disruption is visible to the application;
- and whether recovery requires creating a new connection.

## Expected Behavior

In the plain TCP case, the original connection is expected to fail after the path or address change. Since TCP connection state is associated with the source and destination IP addresses and port numbers, packets arriving with a different address pair cannot be mapped to the existing connection state. As a result, communication stops unless the application establishes a new connection.

In the TCP reconnect case, the original connection is also expected to fail, but the application attempts to recover explicitly. This case therefore does not preserve transport-level continuity. Instead, it measures how quickly communication can resume when recovery is handled above the transport layer. This baseline is useful because many real applications can tolerate failures by reconnecting, even though the underlying transport connection has been lost.

In the QUIC case, the connection is expected to survive the path or address change if migration succeeds. QUIC connection identifiers allow packets from the new path to remain associated with the existing connection, while path validation tests whether the new path can be used for continued communication. Therefore, QUIC is expected to preserve transport-level continuity more effectively than either TCP case, although a short disruption may still occur while the path change is detected and validated.

## Results
