# Simple IMC Messaging Protocol (SIMP) Implementation

This project implements a basic messaging protocol called SIMP (Simple IMC Messaging Protocol) over UDP. It includes a daemon and a client application, allowing users to establish chat connections and exchange messages.

## Project Structure

The project consists of the following files:

*   `simp_daemon.py`: The SIMP daemon application that runs in the background, manages client connections, and routes messages.
*   `simp_client.py`: The SIMP client application that users interact with to initiate chats and send messages.
*   `README.md`: This file, providing information about the project.

## SIMP Protocol Specification

The SIMP protocol is designed as a lightweight messaging protocol over UDP. It uses a three-way handshake for connection establishment, stop-and-wait for reliable message delivery, and has mechanisms for handling errors.

### Datagram Types

*   **Control Datagram (0x01):** Used for connection management (SYN, ACK, FIN) and error handling.
*   **Chat Datagram (0x02):** Used to send chat messages between users.

### Header Format

Each datagram consists of a header followed by an optional payload. The header is 39 bytes long:

| Field        | Size (bytes) | Description                                                                   |
|--------------|--------------|-------------------------------------------------------------------------------|
| Type         | 1            | Datagram type (0x01 for control, 0x02 for chat)                               |
| Operation    | 1            | Operation code (e.g., SYN, ACK, FIN, ERR)                                     |
| Sequence     | 1            | Sequence number (0x00 or 0x01 for resend detection)                            |
| Username     | 32           | User's username (ASCII encoded, padded with spaces)                           |
| Length       | 4            | Length of the payload in bytes (big-endian)                                   |

### Payload

The payload content depends on the datagram type:
* For control messages, the payload can be:
    * a readable error message if Operation is `ERR`
    * a target address in the format "IP:PORT" if the Operation is `SYN`
* For chat messages, the payload is the ASCII text message to be delivered.

### Connection Establishment

SIMP uses a three-way handshake to establish connections:
 1. The sender sends a `SYN` control datagram to the destination address including the target address.
 2. The receiver sends a `SYN + ACK` control datagram back to the sender.
 3. The sender sends an `ACK` to acknowledge the `SYN+ACK`.

### Message Delivery

*   Messages are sent using a stop-and-wait approach. The sender waits for an `ACK` before sending the next message.
*   If an `ACK` is not received within 5 seconds (timeout), the message is retransmitted using the same sequence number.
*   The sequence numbers 0x00 and 0x01 are used in a cyclical manner, to identify resent or lost datagrams.

### Connection Termination
*   A connection is terminated when a user sends a `FIN` control message to the other user.
*   The other user must send an `ACK` in response, and then the connection is closed.

### Error Handling

*   If a user tries to connect while already in a chat, the daemon responds with an `ERR` control message with the error description `User already in another chat`.
*   If a user tries to send a chat message when it is not part of an active chat, this message will be ignored.

## Running the Project

To run the project:

1.  **Start the Daemon:**
    ```bash
    python simp_daemon.py
    ```

    This will start the SIMP daemon listening on port 7777.

2.  **Start the Client(s):**
     Open a new terminal window for each client, and launch the following command, changing the daemon IP as needed, and the port which each client will use for communication:
    ```bash
    python simp_client.py
    ```

    The client will prompt you for the daemon's IP address and its own port.

    The client will prompt for a username.

3.  **Initiate a chat:**
     Type `start` and enter the IP and port of the other client in the format `IP:PORT`

4.  **Send Messages:**
      Type `send <your message>` to send a chat message.

5.  **Q:**
      Type `q` to end a session and disconnect from the daemon.

## Important Implementation Notes

*   **Daemon and Client Separation:** The daemon and client are independent processes that communicate over the network, so a communication protocol must be implemented.
*   **Synchronization:** The chat operation is synchronous, i.e. after sending a message, the client waits indefinitely for a response.
*   **Address Binding:** The daemon binds to any available address, using port 7777, and the client binds to the specific port provided by the user.
*   **Port Standardization**: The port used for client to daemon and daemon to daemon communication is standarized.
*   **Username**: The username is padded with spaces so that it occupies 32 bytes on the header.

## Requirements

*   Python 3.6 or later

## Dependencies
The project has no other dependencies.

## Authors

*   Ali Aliyev
*   Xander Smakman