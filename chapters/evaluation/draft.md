
The previous sections described how QUIC connection migration addresses identity-location coupling at the transport layer. This section examines the same issue through a small-scale exploratory evaluation of plain TCP, a best-case TCP reconnect, and QUIC. The comparison concerns their behavior after a client path or address change during an ongoing session.

The experiments were not repeated systematically enough to support strong quantitative conclusions about latency or recovery time. The observations are used mainly for a qualitative comparison of the three approaches. Particular attention is given to whether the original transport connection survives the network change and whether communication requires a new connection.

## Experimental Setup

The experiments use a controlled Mininet topology to emulate a path or address change during an active client-server session. The client and server first communicate over the initial path. A forced path or address change is then introduced while the session remains active.

\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{mn.png}
\captionof{figure}{Screenshot of the running Mininet topology.}
\label{fig:mn}
\end{center}

Three cases were tested. The first uses plain TCP, which has no support for connection migration. The second uses TCP with a hard-coded reconnect mechanism. When the network change is triggered, the application already knows the address required for the replacement connection and can attempt a new TCP connection directly. The hard-coded address removes address discovery from the reconnect procedure and provides a deliberately favorable TCP baseline. The third case uses QUIC connection migration.

The same network event is used for each case. Plain TCP has no recovery mechanism. The best-case TCP reconnect replaces the failed transport connection with another connection to a known address. QUIC attempts to preserve the existing transport connection across the address change.

The main question is whether the original transport connection survives the network change. The experiments also record whether another connection has to be created, what interruption is visible at the application, and approximately how long communication takes to resume. The timing values are treated only as preliminary observations.

## Expected Behavior

In the plain TCP case, the original connection is expected to fail after the path or address change. TCP associates the connection with the source and destination IP addresses and port numbers. Packets with a different address pair no longer correspond to the same TCP connection, so communication cannot continue through that connection.

In the best-case TCP reconnect case, the original connection is also expected to fail. The replacement address is already known to the application, so no address discovery is required before another connection can be created. The reconnect is triggered directly after the network change. This case provides a favorable application-level recovery baseline rather than a model of all TCP-based applications.

In the QUIC case, the existing connection is expected to survive if migration succeeds. Connection identifiers allow packets from the new path to remain associated with the established QUIC connection. Path validation determines whether that path can support continued communication. The comparison places QUIC migration against a TCP reconnect case in which address-discovery overhead has already been removed.

## Results

The number of attempts was too small for a strong quantitative comparison of recovery time. The measurements are treated as preliminary observations rather than benchmark results.

\begin{table}[h]
\centering
\caption{Preliminary comparison after path or address change.}
\label{tab:evaluation-results}
\begin{tabular}{p{0.25\linewidth} p{0.20\linewidth} p{0.24\linewidth} p{0.20\linewidth}}
\hline
\textbf{Criterion} & \textbf{Plain TCP} & \textbf{Best-case TCP reconnect} & \textbf{QUIC} \\
\hline
Transport continuity
& No
& No
& Yes, if migration succeeds \\

Connection needed for recovery
& Yes
& Yes
& No, if migration succeeds \\

Recovery mechanism
& None
& New TCP connection to known IP
& QUIC connection migration \\

Visible behavior
& Communication stops
& Communication resumes after reconnect
& Communication continues after migration \\

Timing observation
& No recovery
& No noticeable difference from QUIC
& No noticeable difference from TCP reconnect \\
\hline
\end{tabular}
\end{table}

The plain TCP case behaved as expected. The original connection could no longer continue after the path or address change. Its identity remained associated with the previous four-tuple, so the network change broke transport-level continuity.

The best-case TCP reconnect restored communication through a new TCP connection. The application already knew the replacement address and could attempt the new connection directly after the network change. The original TCP connection was not preserved.

The QUIC case retained the existing transport connection when migration succeeded. Packets from the new path remained associated with that connection through the connection identifier, and path validation allowed communication to continue over the replacement path. No replacement transport connection was required.

No noticeable difference in recovery time was observed between the best-case TCP reconnect and QUIC migration in the preliminary attempts. The TCP baseline already knew the replacement address and could initiate another connection directly. The experiment did not show a visible timing advantage for QUIC under this deliberately favorable reconnect condition.

The TCP baseline restored communication through a new connection. Successful QUIC migration kept the existing transport connection.

## Discussion

Recovery time did not noticeably differ between the best-case TCP reconnect and QUIC migration in the attempts performed. The TCP baseline removed address discovery from the reconnect procedure. The destination address was already known, and the reconnect could start directly after the network change.

The experiment does not provide evidence that QUIC migration is faster than an optimized reconnect under the tested conditions. Its observable difference lies in the treatment of the transport connection. TCP reconnect restores communication after the original connection has failed and uses a new connection for subsequent traffic. QUIC migration can continue through the existing connection after the path or address change.

The limited number of attempts places a clear limit on the conclusions that can be drawn. The experiment does not establish a general recovery-time relationship between QUIC migration and TCP reconnect. More repetitions and a wider range of network conditions would be required for a quantitative comparison.

## Summary

Plain TCP did not preserve the original connection after the forced path or address change. The best-case TCP reconnect restored communication through a new connection to an address that was already known to the application. QUIC retained the existing transport connection when migration succeeded.

The experiment provides a narrow comparison of the identity-location coupling discussed in this thesis. The best-case TCP reconnect restores communication after the address-bound connection has been lost. QUIC migration can preserve the transport connection itself across the path or address change.
