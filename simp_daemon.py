import socket
import threading
import json
import logging

# Configuration
DAEMON_PORT = 7777
CLIENT_PORT = 7778

# In-memory storage for active connections
active_chats = {}

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    # Create a UDP socket for the daemon
    daemon_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    daemon_socket.bind(("", DAEMON_PORT))

    logging.info(f"SIMP Daemon started and listening on port {DAEMON_PORT}.")

    try:
        while True:
            data, addr = daemon_socket.recvfrom(1024)
            threading.Thread(target=handle_request, args=(daemon_socket, data, addr)).start()
    except KeyboardInterrupt:
        logging.info("Daemon terminated by user.")
    finally:
        daemon_socket.close()

def handle_request(daemon_socket, data, addr):
    try:
        message = json.loads(data.decode())
        message_type = message.get("type")

        if message_type == "register":
            username = message.get("username")
            logging.info(f"Registered client '{username}' at {addr}.")

        elif message_type == "chat_request":
            target_ip = message.get("target_ip")
            if target_ip in active_chats:
                error_message = {
                    "type": "error",
                    "message": "User already in another chat."
                }
                daemon_socket.sendto(json.dumps(error_message).encode(), addr)
            else:
                active_chats[addr[0]] = target_ip
                logging.info(f"Chat request from {addr[0]} to {target_ip}.")
                relay_chat_request(daemon_socket, target_ip, addr)

        elif message_type == "chat_accept":
            target_ip = message.get("target_ip")
            logging.info(f"Chat accepted between {addr[0]} and {target_ip}.")
            active_chats[addr[0]] = target_ip
            notify_chat_acceptance(daemon_socket, target_ip, addr)

        elif message_type == "chat_decline":
            target_ip = message.get("target_ip")
            logging.info(f"Chat declined by {addr[0]} for {target_ip}.")

        elif message_type == "chat_message":
            relay_chat_message(daemon_socket, message, addr)

        elif message_type == "quit":
            logging.info(f"Client at {addr[0]} disconnected.")
            if addr[0] in active_chats:
                del active_chats[addr[0]]

    except Exception as e:
        logging.error(f"Error handling request from {addr}: {e}")

def relay_chat_request(daemon_socket, target_ip, origin):
    chat_request = {
        "type": "chat_request",
        "username": "User",
        "origin_ip": origin[0]
    }
    daemon_socket.sendto(json.dumps(chat_request).encode(), (target_ip, CLIENT_PORT))

def notify_chat_acceptance(daemon_socket, target_ip, origin):
    acceptance_message = {
        "type": "chat_accept",
        "message": "Chat request accepted."
    }
    daemon_socket.sendto(json.dumps(acceptance_message).encode(), (target_ip, CLIENT_PORT))

def relay_chat_message(daemon_socket, message, origin):
    target_ip = active_chats.get(origin[0])
    if target_ip:
        daemon_socket.sendto(json.dumps(message).encode(), (target_ip, CLIENT_PORT))
    else:
        error_message = {
            "type": "error",
            "message": "Target user not available."
        }
        daemon_socket.sendto(json.dumps(error_message).encode(), origin)

if __name__ == "__main__":
    main()
