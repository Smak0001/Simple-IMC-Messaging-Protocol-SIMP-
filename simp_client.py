import socket
import argparse
import logging
import json

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="SIMP Client")
    parser.add_argument("daemon_ip", help="IP address of the SIMP daemon")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    # Define client-to-daemon communication port
    CLIENT_PORT = 7778
    DAEMON_PORT = 7777

    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("", CLIENT_PORT))

    logging.info(f"SIMP Client started. Bound to port {CLIENT_PORT}.")

    try:
        # Register with the daemon
        username = input("Enter your username: ")
        registration_message = {
            "type": "register",
            "username": username
        }
        client_socket.sendto(json.dumps(registration_message).encode(), (args.daemon_ip, DAEMON_PORT))

        while True:
            print("Options:")
            print("1. Start a new chat")
            print("2. Wait for chat requests")
            print("q. Quit")
            choice = input("Enter your choice: ")

            if choice == "1":
                target_ip = input("Enter the IP address of the user to chat with: ")
                chat_request = {
                    "type": "chat_request",
                    "target_ip": target_ip
                }
                client_socket.sendto(json.dumps(chat_request).encode(), (args.daemon_ip, DAEMON_PORT))

            elif choice == "2":
                logging.info("Waiting for incoming chat requests...")
                while True:
                    data, addr = client_socket.recvfrom(1024)
                    message = json.loads(data.decode())

                    if message.get("type") == "chat_request":
                        print(f"Chat request received from {message['username']} ({addr[0]}).")
                        response = input("Accept (y/n)? ")
                        if response.lower() == "y":
                            accept_message = {
                                "type": "chat_accept",
                                "target_ip": addr[0]
                            }
                            client_socket.sendto(json.dumps(accept_message).encode(), (args.daemon_ip, DAEMON_PORT))
                            chat(client_socket, addr[0])
                        else:
                            decline_message = {
                                "type": "chat_decline",
                                "target_ip": addr[0]
                            }
                            client_socket.sendto(json.dumps(decline_message).encode(), (args.daemon_ip, DAEMON_PORT))
                            logging.info("Chat request declined.")
                        break

            elif choice == "q":
                quit_message = {
                    "type": "quit"
                }
                client_socket.sendto(json.dumps(quit_message).encode(), (args.daemon_ip, DAEMON_PORT))
                logging.info("Exiting SIMP Client.")
                break

            else:
                print("Invalid option. Please try again.")

    except KeyboardInterrupt:
        logging.info("Client terminated by user.")
    finally:
        client_socket.close()

def chat(client_socket, target_ip):
    print("Chat session started. Type 'exit' to end the chat.")
    while True:
        message = input("You: ")
        if message.lower() == "exit":
            logging.info("Chat session ended.")
            break
        chat_message = {
            "type": "chat_message",
            "message": message
        }
        client_socket.sendto(json.dumps(chat_message).encode(), (target_ip, 7777))

if __name__ == "__main__":
    main()
