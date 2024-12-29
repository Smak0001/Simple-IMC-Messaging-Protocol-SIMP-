import socket
import threading
import time

# Constants
CONTROL_PORT = 7777
SEQUENCE_NUMBERS = [0x00, 0x01]
DAEMON_PORT = 7777
TIMEOUT = 5  # Timeout for stop-and-wait in seconds


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


# SIMP Client
class SIMPClient:
    def __init__(self, daemon_ip, client_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", client_port))
        self.daemon_ip = daemon_ip
        self.username = ""
        self.sequence = 0x00
        self.chat_started = False
        self.waiting_for_ack = False
        self.last_sent_message = None


    def send_control_message(self, operation, payload=""):
        header = create_header(0x01, operation, self.sequence, self.username, len(payload))
        message = header + payload.encode('ascii')
        self.socket.sendto(message, (self.daemon_ip, DAEMON_PORT))
        return message


    def send_chat_message(self, message):
        header = create_header(0x02, 0x01, self.sequence, self.username, len(message))
        datagram = header + message.encode('ascii')
        self.socket.sendto(datagram, (self.daemon_ip, DAEMON_PORT))
        self.last_sent_message = datagram
        self.waiting_for_ack = True
        return datagram


    def resend_last_message(self):
        if self.last_sent_message:
          print("Resending message...")
          self.socket.sendto(self.last_sent_message, (self.daemon_ip, DAEMON_PORT))


    def receive_messages(self):
        while True:
            try:
                message, _ = self.socket.recvfrom(1024)
                datagram_type, operation, sequence, username, length = parse_header(message[:39])
                payload = message[39:].decode('ascii')

                if datagram_type == 0x01:
                    if operation == 0x01: # ERR
                        print(f"Error: {payload}")
                    elif operation == 0x04: # ACK
                        if self.waiting_for_ack:
                            print("Chat message confirmed")
                            self.waiting_for_ack = False
                            self.sequence = SEQUENCE_NUMBERS[(SEQUENCE_NUMBERS.index(self.sequence) + 1) % 2]
                        elif not self.chat_started:
                           print("Chat confirmed")
                           self.chat_started = True
                    elif operation == 0x06:  # SYN + ACK
                            print("Received SYN+ACK")
                            self.send_control_message(0x04) # Send ACK
                            self.chat_started = True
                            print("Chat confirmed")



                elif datagram_type == 0x02:
                    print(f"[{username}] {payload}")


            except Exception as e:
                print(f"Error receiving message: {e}")


    def run(self):
        self.username = input("Enter your username: ").strip()
        threading.Thread(target=self.receive_messages, daemon=True).start()

        while True:
            command = input("Enter command (start, send, quit): ")
            if command == "start":
                target = input("Enter target IP and port (e.g., 127.0.0.1:5000): ").strip()
                print("Sending SYN")
                self.send_control_message(0x02, target) #Send SYN
                start_time = time.time()
                while not self.chat_started:
                    if time.time() - start_time > TIMEOUT:
                        print("Timeout, resending SYN")
                        self.send_control_message(0x02, target)
                        start_time = time.time()
                    time.sleep(0.1)

            elif command.startswith("send "):
                message = command[5:]
                self.send_chat_message(message)
                start_time = time.time()

                while self.waiting_for_ack:
                   if time.time() - start_time > TIMEOUT:
                        self.resend_last_message()
                        start_time = time.time()
                   time.sleep(0.1)

            elif command == "quit":
                self.send_control_message(0x08)
                break
        self.socket.close()

if __name__ == "__main__":
    daemon_ip = input("Enter daemon IP address: ").strip()
    client_port = int(input("Enter the port you want to bind to: ").strip())
    client = SIMPClient(daemon_ip, client_port)
    client.run()