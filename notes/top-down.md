When one end system has data to send to another end system, the sending end sys- tem segments the data and adds header bytes to each segment. The resulting pack- ages of information, known as packets in the jargon of computer networks, are then sent through the network to the destination end system, where they are reassembled into the original data.

The sequence of communication links and packet switches traversed by a packet from the sending end system to the receiving end system is known as a route or path through the network.

Internet standards are developed by the Internet Engineering Task Force (IETF)[IETF 2012]. The IETF standards documents are called requests for comments (RFCs).

Transmission Control Protocol (TCP)
User Datagram Protocol (UDP)
Internet Protocol (IP)
Application Programming Interface (API)

The IP protocol specifies the format of the packets that are sent and received among routers and end systems.

A protocol defines the format and the order of messages exchanged between two or more communicating entities, as well as the actions taken on the trans- mission and/or receipt of a message or other event.

TCP socket is identified by a four-tuple: (source IP address, source port number, destination IP address, destination port number). Thus, when a TCP segment arrives from the network to a host, the host uses all four values to direct (demultiplex) the segment to the appropriate socket.
