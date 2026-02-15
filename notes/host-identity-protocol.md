> HIP enhances the original Internet architecture by adding a name space used between the IP layer and the transport protocols. This new name space consists of cryptographic identifiers, thereby implementing the so-called identifier / locator split.

- Adds new namespace
- Inserted between IP and transport
- Uses cryptographic identifiers
- Clean separation of:
	- Identity (Host Identifier)
	- Location (IP address)

> In the current IP architecture the IP addresses assume the dual role of acting both as host identifiers and locators... in HIP these two roles are cleanly separated.

- Internet historically conflated identity and location
- Help define location, identity and session binding
- "Identity ≠ Location" anchor

> Compared to the original Internet, perhaps the largest problem... is the loss of connectivity, caused by NATs, firewalls, and dynamic IP addresses.

- End-to-end transparency lost
- IP no longer globally stable
- Address ≠ stable identifier anymore

> The so-called classical network-layer addressing invariants... have been eroded by the use of private address space (NAT for IPv4)...

- Classical invariants
- Being eroded by NAT
- Architectural degradation, not just engineering inconvenience

> Effective mobility support requires a level of indirection... to map the mobile entity's stable name to its dynamic, changing location.

- Mobility = mapping problem
- Stable name -> dynamic locator
- Requires indirection layer

> HIP attempts to... restore... the four classical network-layer addressing invariants...

- Non-mutability, location independence, reversibility, omnisciency
- Attempt to restore lost architectural properties
- Rebuild invariants at a different layer

> The HIP architecture offers a possible path for overcoming these limitations by providing a new end-to-end naming invariant and protocol mechanisms that allow the IP addresses used on a wire to be used as ephemeral locators rather than host identifiers themselves.

- Architectural shift
- IP address downgraded to:
	- Wire-level routing artifact
	- Ephemeral locator
- End-to-end identity restored at higher layer

> The Host Identifiers (HI) are public cryptographic keys, allowing hosts to authenticate their peer hosts directly by their HI.

- Identity is self-certifying
- Identity is cryptographically bound
- Authentication becomes architectural, not optional add-on

> HIP cleanly separates host-to-host signalling and data traffic into separate planes...

- Control/data separation
- For multipath discussion

> HIP can be seen as restoring the now-lost end-to-end connectivity...

- Restoration of original architectural intent
- Under modern constraints (NAT, mobility, multi-homing)

> HIP explicitly adds a new layer of indirection and a new name space, thereby adding the needed level of indirection to the architecture.

- Mobile IP = reuse same namespace
- HIP = introduce new namespace

> The current HIP aim can be characterised as providing the lowest layer in the stack that encompasses location-independent identifiers and end-to-end connectivity.

- HIP architectural goal
