import socket
import threading

# Stores clients as:
# { username: (ip, tcp_port, udp_port) }
clients = {}

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000


def handle_client(conn, addr):
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            parts = data.split("|")

            # REGISTER|username|tcp|udp
            if parts[0] == "REGISTER":
                username = parts[1]
                tcp_port = parts[2]
                udp_port = parts[3]

                clients[username] = (addr[0], tcp_port, udp_port)
                print(f"[REGISTER] {username} -> {clients[username]}")

                conn.send("OK".encode())

            # REQUEST_LIST
            elif parts[0] == "REQUEST_LIST":
                response = ""
                for user, info in clients.items():
                    response += f"{user},{info[0]},{info[1]},{info[2]}|"

                conn.send(response.encode())

        except Exception as e:
            print(f"[ERROR] {e}")
            break

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()

    print(f"[SERVER] Running on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        print(f"[CONNECTION] {addr}")

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
