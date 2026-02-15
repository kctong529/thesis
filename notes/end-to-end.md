> The function in question can completely and correctly be implemented only with the knowledge and help of the application standing at the endpoints of the communication system. Therefore, providing that questioned function as a feature of the communication system itself is not possible.

- TCP assumed stable endpoints
- Reliability and state live end-to-end
- But identity was implicitly bound to IP
- QUIC preserves end-to-end semantics but changes how endpoints are identified

> The extra effort expended in the communication system to provide a guarantee of reliable data transmission is only reducing the frequency of retries by the file transfer application; it has no effect on inevitability or correctness of the outcome...

- Reliability must ultimately be ensured end-to-end
- Lower-layer guarantees cannot eliminate the need for end-level correctness
- Transport-layer mechanisms are fundamentally performance optimizations
- TCP reliability is not logically sufficient to define session correctness

> What the application wants to know is whether or not the target host acted on the message... The acknowledgment that is really desired is an end-to-end one...

- Help define session state
- End-to-end semantic correctness
- Transport guarantees do not equal application semantics

> Much of the debate in the network protocol community over datagrams, virtual circuits, and connectionless protocols is a debate about end-to-end arguments.

> Against making any function a permanent fixture of lower level modules; the function may be provided by a lower level module, but it should always be replaceable by an application's special version of the function.

- Why TCP becoming kernel-embedded created rigidity
- Why QUIC relocates transport to user space
- Why encrypted transport headers prevent middlebox dependence
- Connect end-to-end reasoning directly to evolvability
