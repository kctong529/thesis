> "These two subflows are linked together inside a single MultiPath TCP connection and both can be used to send data. Subflows may fail and be added during the lifetime of a MultiPath TCP connection."

- A connection can span multiple paths
- Identity ≠ single location

> "The key to retrieve a listener is no longer the usual TCP 5-tuple, but instead a token attached in a TCP option."

- Even MPTCP begins to weaken the 5-tuple as sole identity
- Even within TCP, extensions started introducing explicit identifiers
