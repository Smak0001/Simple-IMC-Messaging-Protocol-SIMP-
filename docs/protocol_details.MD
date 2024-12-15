# SIMP Protocol Details

## **Introduction**
The Simple IMC Messaging Protocol (SIMP) is a lightweight messaging protocol designed for reliable chat applications operating over UDP. This document provides a detailed specification of the protocol, outlining the datagram format, connection management, message delivery mechanisms, and operational guidelines.

---

## **Datagram Format**
Each SIMP datagram consists of a **header** and a **payload**.

### **Header Fields**
1. **Type (1 byte)**: Specifies the type of datagram.
   - `0x01`: Control datagram.
   - `0x02`: Chat datagram.

2. **Operation (1 byte)**: Indicates the specific operation.
   - If `Type == 0x01`:
     - `0x01`: Error (`ERR`).
     - `0x02`: Synchronization (`SYN`).
     - `0x04`: Acknowledgment (`ACK`).
     - `0x08`: Finish (`FIN`).
   - If `Type == 0x02`:
     - `0x01`: Chat operation (fixed).

3. **Sequence (1 byte)**: Sequence number for tracking datagrams (0 or 1).

4. **User (32 bytes)**: The username of the sender, encoded as an ASCII string.

5. **Length (4 bytes)**: The size of the payload in bytes.

### **Payload**
The content of the payload depends on the `Type` field:
- **Control Datagram**:
  - If `Operation == ERR`: A human-readable error message (ASCII).
- **Chat Datagram**:
  - The chat message content.

---

## **Connection Management**
SIMP establishes and terminates connections using control datagrams and a three-way handshake mechanism.

### **Three-Way Handshake**
1. **SYN (Client to Server)**: Initiates the connection.
2. **SYN + ACK (Server to Client)**: Acknowledges and synchronizes.
3. **ACK (Client to Server)**: Completes the handshake.

If the server declines the connection, it sends a `FIN` datagram instead of `SYN + ACK`.

### **Connection Termination**
A user terminates the connection by sending a `FIN` datagram. The recipient acknowledges with an `ACK` before closing.

---

## **Reliable Delivery Mechanism**
### **Stop-and-Wait Protocol**
- The sender transmits a datagram and waits for an acknowledgment (`ACK`).
- If no `ACK` is received within 5 seconds, the sender retransmits the datagram with the same sequence number.
- Sequence numbers alternate between `0` and `1` to differentiate between retransmissions.

---

## **Error Handling**
1. **Busy User**: If a user is already engaged in a chat, incoming connection requests are rejected with:
   - `ERR`: "User already in another chat."
   - Followed by a `FIN` datagram.
2. **Unreachable User**: If a user cannot be contacted, an appropriate error message is sent.

---

## **Operational Guidelines**
1. **Daemon**
   - Listens on port `7777` for other daemons.
   - Communicates with the local client on port `7778`.

2. **Client**
   - Sends chat requests to the daemon.
   - Provides options to accept, decline, or initiate chats.
   - Supports synchronous message exchange.

3. **Message Exchange**
   - The chat message payloads are synchronous.
   - Each message must be acknowledged by the recipient before the next is sent.

---

## **Protocol Example**
### **Connection Establishment**
1. Client A sends: `SYN` to Server B.
2. Server B responds: `SYN + ACK`.
3. Client A completes: `ACK`.

### **Message Exchange**
1. Client A sends: Chat message (sequence `0`).
2. Server B responds: `ACK`.
3. Server B sends: Chat message (sequence `1`).

### **Connection Termination**
1. Client A sends: `FIN`.
2. Server B responds: `ACK` and closes connection.

---

## **Implementation Notes**
- The daemon (`simp_daemon.py`) and client (`simp_client.py`) communicate over standard UDP sockets.
- Daemon-daemon communication always uses port `7777`.
- Daemon-client communication uses port `7778`.
- ASCII encoding is used for all text fields.

---

## **Submission Instructions**
- **Files**:
  - `simp_daemon.py`
  - `simp_client.py`
  - `requirements.txt`
  - Documentation (this PDF and README).
- **Deadline**: 19/12/2024 23:59 via MS-Teams.

---

## **Contact Information**
For questions or issues, contact the course instructor or teaching assistants via the course platform.

