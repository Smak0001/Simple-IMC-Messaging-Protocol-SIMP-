# README: Simple IMC Messaging Protocol (SIMP) Implementation

## Overview
This project implements a lightweight messaging protocol, the Simple IMC Messaging Protocol (SIMP), designed for chat applications using UDP. The protocol includes functionality for reliable message delivery, user communication, and connection management.

The implementation consists of two components:
1. **Daemon (`simp_daemon.py`)**: A background service managing incoming chat requests and message exchanges.
2. **Client (`simp_client.py`)**: A text-based interface for end-users to initiate and participate in chats.

---

## Features
- **Three-Way Handshake**: Ensures proper connection establishment between users.
- **Reliable Delivery**: Messages are retransmitted using stop-and-wait strategy if acknowledgments are not received.
- **Synchronous Communication**: Users exchange messages synchronously.
- **Error Handling**: Rejects chat requests when users are busy, with appropriate error messages.
- **User-Friendly Interface**: Provides intuitive options to start or accept chats.

---

## Requirements
- Python 3.8+
- Libraries specified in `requirements.txt`.

---

## Installation
1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
### **Daemon**
Start the daemon on a server with the following command:
```bash
python simp_daemon.py <server_ip>
```
- **Server IP**: The IP address the daemon will bind to.

### **Client**
Run the client on the user's machine:
```bash
python simp_client.py <daemon_ip>
```
- **Daemon IP**: The IP address of the daemon to connect to.

### **Chat Workflow**
1. **Daemon**: Always runs in the background, listening on port `7777` for incoming chat requests.
2. **Client**:
   - If no chat request is pending, the client can:
     - Initiate a new chat by providing the recipient's IP address.
     - Wait for incoming chat requests.
   - If a chat request is received, the client can:
     - Accept or decline the request.
   - Press `q` to quit and disconnect from the daemon.

---

## Technical Details
1. **Protocol Header**
   - Type: Indicates Control (`0x01`) or Chat (`0x02`) datagram.
   - Operation: Defines actions like SYN, ACK, FIN, etc.
   - Sequence: Tracks message sequence numbers (0 or 1).
   - User: 32-byte ASCII string for the username.
   - Length: Size of the payload in bytes.

2. **Message Handling**
   - Control messages manage connection states.
   - Chat messages carry the text content.

3. **Ports**
   - Daemon-to-daemon: `7777`
   - Client-to-daemon: `7778`

---

## Assessment Criteria
1. **Message Implementation (15 points)**: Correct formatting and parsing of headers and payloads.
2. **Three-Way Handshake (10 points)**: Accurate implementation for establishing connections.
3. **Stop-and-Wait (10 points)**: Reliable delivery of messages with retransmissions.
4. **Daemon-Client Communication (10 points)**: Robust interaction between the client and daemon.
5. **Code Quality (5 points)**: Clean, well-documented, and maintainable code.

---

## Submission
Submit the following in a ZIP file by **19/12/2024 23:59** via MS-Teams:
- `simp_daemon.py`: Daemon implementation.
- `simp_client.py`: Client implementation.
- `requirements.txt`: Dependency file.
- Documentation folder with this README and the protocol PDF.

---

## Contact
For any questions or issues, reach out to the course instructor or teaching assistants via the course platform.

