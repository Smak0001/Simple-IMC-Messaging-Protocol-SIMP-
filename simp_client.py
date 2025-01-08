import socket
import threading
import time
import sys

# Constants
CONTROL_PORT = 7777
SEQUENCE_NUMBERS = [0x00, 0x01]
DAEMON_PORT = 7777
TIMEOUT = 5  # Timeout for stop-and-wait in seconds
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
		self.is_running = True
		self.waiting_for_connection = False
		self.pending_request = None

	def send_control_message(self, operation, payload=""):
		header = create_header(0x01, operation, self.sequence, self.username, len(payload))
		message = header + payload.encode('ascii')
		try:
			self.socket.sendto(message, (self.daemon_ip, DAEMON_PORT))
		except Exception as e:
			print(f"Error sending control message: {e}")
		return message

	def send_chat_message(self, message):
		header = create_header(0x02, 0x01, self.sequence, self.username, len(message))
		datagram = header + message.encode('ascii')
		try:
			self.socket.sendto(datagram, (self.daemon_ip, DAEMON_PORT))
			self.last_sent_message = datagram
			self.waiting_for_ack = True
		except Exception as e:
			print(f"Error sending chat message: {e}")
		return datagram

	def resend_last_message(self):
		if self.last_sent_message:
			print("Resending message...")
			try:
				self.socket.sendto(self.last_sent_message, (self.daemon_ip, DAEMON_PORT))
			except Exception as e:
				print(f"Error resending message: {e}")

	def receive_messages(self):
		while self.is_running:
			try:
				message, _ = self.socket.recvfrom(1024)
				datagram_type, operation, sequence, username, length = parse_header(message[:39])
				payload = message[39:].decode('ascii')

				if datagram_type == 0x01:
					if operation == ERR:  # ERR
						print(f"Error: {payload}")
						self.waiting_for_ack = False  # exit the send loop
					elif operation == ACK:  # ACK
						if self.waiting_for_ack:
							print("Chat message confirmed")
							self.waiting_for_ack = False
							# Rotate sequence number 0 -> 1, 1 -> 0
							self.sequence = SEQUENCE_NUMBERS[
								(SEQUENCE_NUMBERS.index(self.sequence) + 1) % 2
							]
						elif not self.chat_started:
							print("Chat confirmed")
							self.chat_started = True
					elif operation == (SYN | ACK):  # SYN + ACK
						print("Received SYN+ACK")
						self.send_control_message(ACK)  # Send ACK
						self.chat_started = True
						print("Chat confirmed")
					elif operation == SYN:  # Incoming chat request
						print(f"Incoming chat request from {username} at {payload}")
						self.pending_request = (username, payload)
						self.waiting_for_connection = False

				elif datagram_type == 0x02:
					print(f"[{username}] {payload}")

			except Exception as e:
				if self.is_running:
					print(f"Error receiving message: {e}")

	def run(self):
		self.username = input("Enter your username: ").strip()
		threading.Thread(target=self.receive_messages, daemon=True).start()

		while True:
			command = input("Enter command (start, wait, or q to exit immediately): ").strip().lower()

			# Immediately end the application if user presses 'q'
			if command == 'q':
				print("Exiting application now...")
				self.is_running = False
				self.socket.close()  # Make sure socket is closed
				sys.exit(0)          # Immediately terminate

			if command == "start":
				target = input("Enter target IP and port (e.g., 127.0.0.1:5000): ").strip()
				print("Sending SYN")
				self.send_control_message(SYN, target)  # Send SYN
				start_time = time.time()
				while not self.chat_started:
					if time.time() - start_time > TIMEOUT:
						print("Timeout, resending SYN")
						self.send_control_message(SYN, target)
						start_time = time.time()
					time.sleep(0.1)

				# Enter chat mode if the connection is established
				while self.chat_started:
					message = input("Enter message (or 'end' to finish chat): ").strip().lower()
					if message == "end":
						self.send_control_message(FIN)
						self.chat_started = False
					elif message == "q":
						self.is_running = False
						self.socket.close()  # Make sure socket is closed
						sys.exit(0)  
					else:
						self.send_chat_message(message)

			elif command == "wait":
				print("Waiting for connection requests...")
				self.waiting_for_connection = True
				while self.waiting_for_connection:
					# Sleep briefly to avoid busy-wait
					time.sleep(0.1)
					if self.pending_request:
						print(f"Chat request from {self.pending_request[0]} at {self.pending_request[1]}")
						response = input("Accept chat request? (yes/no): ").strip().lower()
						if response == "yes":
							self.send_control_message(SYN | ACK, self.pending_request[1])
							self.chat_started = True
						self.pending_request = None
						self.waiting_for_connection = False

				# Enter chat mode if the connection is established
				while self.chat_started:
					message = input("Enter message (or 'end' to finish chat): ").strip().lower()
					if message == "end":
						self.send_control_message(FIN)
						self.chat_started = False
					else:
						self.send_chat_message(message)

			elif command == "quit":
				# Graceful shutdown with FIN
				self.send_control_message(FIN)
				self.is_running = False
				break

		# Clean up
		self.socket.close()


if __name__ == "__main__":
	daemon_ip = input("Enter daemon IP address: ").strip()
	client_port = int(input("Enter the port you want to bind to: ").strip())
	client = SIMPClient(daemon_ip, client_port)
	client.run()
