import socket
import threading

# Constants
CONTROL_PORT = 7777
SEQUENCE_NUMBERS = [0x00, 0x01]
SYN = 0x02
ACK = 0x04
FIN = 0x08
ERR = 0x01
CHAT = 0x02

# Helper functions
def create_header(datagram_type, operation, sequence, username, length):
    username = username.ljust(32)[:32].encode('ascii')
    return bytes([datagram_type, operation, sequence]) + username + length.to_bytes(4, 'big')


def parse_header(header):
    datagram_type = header[0]
    operation = header[1]
    sequence = header[2]
    username = header[3:35].decode('ascii').strip()
    length = int.from_bytes(header[35:39], 'big')
    return datagram_type, operation, sequence, username, length


# SIMP Daemon
class SIMPDaemon:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', CONTROL_PORT))
        self.active_chats = {}  # Username: (address, sequence)
        self.pending_requests = {}  # Address: username
        self.syn_received = {}  # Address: sequence
        self.last_received_sequence = {}  # Address: last received sequence number

    def handle_message(self, message, address):
        try:
            datagram_type, operation, sequence, username, length = parse_header(message[:39])
            payload = message[39:].decode('ascii')

            if address not in self.last_received_sequence:
                self.last_received_sequence[address] = None

            if datagram_type == 0x01:  # Control datagram
                if operation == SYN:  # SYN (Start chat request)
                    if username in self.active_chats:
                        # User is already in a chat
                        response = create_header(0x01, ERR, sequence, username, len("User already in another chat"))
                        response += "User already in another chat".encode('ascii')
                        self.socket.sendto(response, address)
                    elif address in self.syn_received and self.syn_received[address] == sequence:
                        print(f"Duplicate SYN received from {username}, sending ERR.")
                        response = create_header(0x01, ERR, sequence, username, len("Duplicate SYN received"))
                        response += "Duplicate SYN received".encode('ascii')
                        self.socket.sendto(response, address)
                    else:
                        # Add pending chat request
                        self.pending_requests[address] = username
                        response = create_header(0x01, SYN | ACK, sequence, username, 0)  # Send SYN+ACK
                        self.socket.sendto(response, address)
                        self.syn_received[address] = sequence
                        print("Sent SYN+ACK to", username)

                elif operation == ACK:  # ACK
                    if address in self.pending_requests:
                        user = self.pending_requests[address]
                        self.active_chats[user] = (address, sequence)  # Username as Key
                        print("Received ACK from:", user)
                        del self.pending_requests[address]
                        if address in self.syn_received:
                            del self.syn_received[address]

                elif operation == FIN:  # FIN (End chat request)
                    if username in self.active_chats:
                        partner_username = None
                        for usr, (addr, seq) in self.active_chats.items():
                            if addr != address and usr != username:
                                partner_username = usr
                                break
                        if partner_username:
                            partner_address = self.active_chats[partner_username][0]
                            del self.active_chats[username]
                            del self.active_chats[partner_username]
                            print(f"Chat with {username} ended by {username}")
                            ack_response = create_header(0x01, ACK, sequence, username, 0)
                            self.socket.sendto(ack_response, partner_address)  # Send ACK to partner
                        else:
                            print(f"Chat with {username} ended by {username}")
                            del self.active_chats[username]
                    else:
                        print("Chat ended by:", username)

            elif datagram_type == CHAT:  # Chat datagram
                if username in self.active_chats:
                    if sequence == self.last_received_sequence[address]:
                        print(f"Duplicate chat message received from {username}, ignoring.")
                        return
                    partner_address = None
                    for usr, (addr, seq) in self.active_chats.items():
                        if addr != address and usr != username:
                            partner_username = usr
                            partner_address = addr
                            break
                    if partner_address:
                        print(f"Message from {username}: {payload}")  # Log message on the daemon
                        self.socket.sendto(message, partner_address)
                        ack_response = create_header(0x01, ACK, sequence, username, 0)
                        self.socket.sendto(ack_response, address)  # Send ACK
                        self.last_received_sequence[address] = sequence
                    else:
                        print("No partner found for this message")
                else:
                    print(f"Chat message received from {address}, but no active chat found.")

        except Exception as e:
            print(f"Error handling message from {address}: {e}")

    def run(self):
        print("SIMP Daemon running on port", CONTROL_PORT)
        while True:
            try:
                message, address = self.socket.recvfrom(1024)
                threading.Thread(target=self.handle_message, args=(message, address)).start()
            except Exception as e:
                print(f"Error in daemon main loop: {e}")

if __name__ == "__main__":
    daemon = SIMPDaemon()
    daemon.run()