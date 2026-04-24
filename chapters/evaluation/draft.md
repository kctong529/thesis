
The previous sections analyzed how QUIC connection migration is intended to mitigate the identity-location problem at the transport layer. This section complements that analysis with a small-scale exploratory evaluation. The purpose is not to provide a general performance benchmark. Instead, the goal is to compare the behavior of different transport approaches when the client path or address changes during an ongoing session.

The evaluation should be interpreted cautiously. The experiments were not repeated systematically enough to support strong quantitative conclusions about latency or recovery time. Nevertheless, the preliminary attempts provide useful qualitative evidence about the difference between application-level recovery and transport-level continuity.

## Experimental Setup

The experiments use a controlled Mininet topology to emulate a path or address change during an active client-server session. A client and server first communicate normally over one path. After the session has been established, a forced path or address change is introduced while communication is still active. This setup creates a repeatable mobility-like event in which the network attachment changes but the application-level communication goal remains the same.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{mn.png}
\captionof{figure}{Screenshot of the running Mininet topology.}
\label{fig:mn}
\end{center}

Three cases are compared. The first case uses plain TCP, which has no built-in support for connection migration. The second case uses TCP with explicit reconnect, which acts as a best-case application-level recovery baseline. In this case, the original TCP connection is not expected to survive the address change, but the application attempts to recover by opening a new connection. The third case uses QUIC, which supports transport-layer migration through connection identifiers and path validation.

The comparison focuses on the response to the same network event. Plain TCP represents the behavior of a traditional address-bound transport connection. TCP with explicit reconnect represents an application that can detect failure and recover by creating a new transport connection. QUIC represents a transport design in which the original connection may continue across the path change.

The evaluation considers four criteria:

- whether continuity is preserved;
- whether recovery requires a new connection;
- how much disruption is visible to the application;
- how long communication takes to resume in the preliminary attempts.

## Expected Behavior

In the plain TCP case, the original connection is expected to fail after the path or address change. Since TCP connection state is associated with the source and destination IP addresses and port numbers, packets arriving with a different address pair cannot be mapped to the existing connection state. As a result, communication stops unless the application establishes a new connection.

In the TCP reconnect case, the original connection is also expected to fail, but the application attempts to recover explicitly. This case does not preserve transport-level continuity. Instead, it measures how quickly communication can resume when recovery is handled above the transport layer. This baseline is useful because many real applications can tolerate failures by reconnecting, even though the underlying transport connection has been lost.

In the QUIC case, the connection is expected to survive the path or address change if migration succeeds. QUIC connection identifiers allow packets from the new path to remain associated with the existing connection. Path validation tests whether the new path can be used for continued communication. As a result, QUIC is expected to preserve transport-level continuity. This does not necessarily imply a shorter visible recovery time than an optimized TCP reconnect baseline.

## Results

Due to the tight schedule, the experiments could not be repeated systematically enough to support a strong quantitative performance comparison. Therefore, the preliminary attempts should be interpreted as exploratory observations rather than benchmark results. They suggest that TCP with explicit reconnect and QUIC migration can restore visible application communication in roughly similar time ranges under the tested best-case conditions.

\begin{table}[h]
\centering
\caption{Preliminary comparison after path or address change.}
\label{tab:evaluation-results}
\begin{tabular}{p{0.28\linewidth} p{0.20\linewidth} p{0.20\linewidth} p{0.20\linewidth}}
\hline
\textbf{Criterion} & \textbf{Plain TCP} & \textbf{TCP reconnect} & \textbf{QUIC} \\
\hline
Transport continuity
& No
& No
& Yes, if migration succeeds \\

New connection needed
& Yes
& Yes
& No, if migration succeeds \\

Visible behavior
& Communication stops
& Communication resumes after reconnect
& Communication continues after validation \\

Timing observation
& No recovery without reconnect
& Similar to QUIC in preliminary attempts
& Similar to TCP reconnect in preliminary attempts \\

Main interpretation
& Address-bound transport fails
& Application-level recovery
& Transport-level continuity \\
\hline
\end{tabular}
\end{table}

The plain TCP case behaved as expected. After the path or address change, the original connection could no longer continue as the same transport connection. The connection identity remained tied to the previous four-tuple. As a result, the address change disrupted transport-level continuity.

The TCP reconnect case restored communication at the application level. However, this recovery required the application to establish a new TCP connection after the original one failed. The recovery did not preserve the original transport connection. It restored the application exchange only after transport failure had occurred.

The QUIC case differed from TCP reconnect in the type of continuity preserved. When migration succeeded, the connection identifier allowed packets from the new path to remain associated with the existing QUIC connection. Path validation then allowed communication to continue on the new path. Thus, QUIC preserved the existing transport connection context. TCP reconnect recovered by creating a new transport connection.

The preliminary timing observations did not show a clear recovery-time advantage for QUIC over the best-case TCP reconnect baseline. The main observed difference was qualitative rather than purely time-based. TCP reconnect can make application communication resume quickly when failure detection and reconnection are efficient. QUIC migration instead preserves transport-level continuity by keeping the existing connection alive across the path change.

## Discussion

The evaluation supports the architectural distinction developed in the previous sections. QUIC migration should not be understood only as a faster recovery mechanism. Its main contribution is that address change can be handled inside an existing transport connection. In contrast, TCP with reconnect treats the address change as a connection failure and recovers above the transport layer.

This distinction matters even when the measured recovery times are similar. A new TCP connection may require new transport state, new congestion-control state, and possibly new security or application-layer setup depending on the protocol stack. A migrated QUIC connection can retain the existing connection context when migration succeeds. Therefore, the application can observe continuity at a different layer of the stack.

At the same time, the preliminary results also limit the strength of the claim. The evaluation does not show that QUIC migration is always faster than TCP reconnect. It also does not establish how QUIC behaves under more demanding network conditions. Delay, loss, bandwidth changes, NAT behavior, implementation policy, and congestion-control adaptation may all affect migration behavior. Therefore, the results should be treated as exploratory evidence rather than as a general benchmark.

## Summary

The exploratory evaluation compared plain TCP, TCP with explicit reconnect, and QUIC under a forced path or address change. Plain TCP did not preserve connection continuity. TCP with reconnect restored application-level communication by creating a new transport connection. QUIC migration preserved the existing transport connection when migration succeeded.

The preliminary attempts suggest that a best-case TCP reconnect can be roughly comparable to QUIC in visible recovery time under controlled conditions. However, this does not make the two approaches equivalent. TCP reconnect provides application-level recovery after transport failure. QUIC migration provides transport-level continuity across path change. Therefore, the evaluation supports the thesis conclusion that QUIC mitigates the identity-location problem at the transport layer. It does not necessarily provide a clear timing advantage in every best-case comparison.
