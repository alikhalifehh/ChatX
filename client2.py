import socket
import threading
import os
import time

import network
from gui import ChatGUI  # GUI

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

USERNAME = "user2"
TCP_PORT = "7000"
UDP_PORT = "7001"


def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    return s


def register():
    s = connect_to_server()
    msg = f"REGISTER|{USERNAME}|{TCP_PORT}|{UDP_PORT}"
    s.send(msg.encode())
    reply = s.recv(1024).decode()
    print("[SERVER REPLY]", reply)
    s.close()


def request_peer_list():
    s = connect_to_server()
    s.send("REQUEST_LIST".encode())
    data = s.recv(4096).decode()

    peers = data.split("|")

    print("\n[FORMATTED PEER LIST]")
    for p in peers:
        if p.strip() == "":
            continue
        user, ip, tcp, udp = p.split(",")
        print(f"{user} -> IP: {ip}, TCP: {tcp}, UDP: {udp}")

    s.close()
    return peers


# =============================
#     TCP LISTENER
# =============================
class TCPListener(threading.Thread):
    def __init__(self, tcp_port, gui):
        super().__init__()
        self.tcp_port = tcp_port
        self.gui = gui
        self.running = True

    def run(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("0.0.0.0", int(self.tcp_port)))
        listener.listen()
        print(f"[TCP LISTENER] Listening on {self.tcp_port}")

        while self.running:
            conn, addr = listener.accept()
            data = conn.recv(4096).decode()
            self.gui.show_message(f"From {addr}: {data}")
            conn.close()


# =============================
#      UDP LISTENER
# =============================
class UDPListener(threading.Thread):
    def __init__(self, udp_port, gui):
        super().__init__()
        self.udp_port = udp_port
        self.gui = gui
        self.running = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", int(self.udp_port)))

        print(f"[UDP LISTENER] Listening on {self.udp_port}")

        filename = None
        chunks = {}

        while True:
            data, addr = sock.recvfrom(65535)

            if data.startswith(b"FILENAME:"):
                filename = data.split(b":", 1)[1].decode()
                chunks = {}
                self.gui.show_message(f"[UDP] Receiving '{filename}'...")
                continue

            if b"EOF" in data:

                if filename is None:
                    continue  # FIXED

                clean = data.replace(b"EOF", b"")

                if clean:
                    seq = max(chunks.keys()) + 1 if chunks else 0
                    chunks[seq] = clean

                ordered = b"".join(chunks[i] for i in sorted(chunks.keys()))

                save_name = os.path.abspath("received_" + filename)
                with open(save_name, "wb") as f:
                    f.write(ordered)

                self.gui.show_message(f"[UDP] File '{save_name}' saved.")
                self.gui.add_clickable_file(save_name)

                filename = None
                chunks = {}
                continue

            if filename is not None:
                seq = int.from_bytes(data[:4], "big")
                chunk_data = data[4:]
                chunks[seq] = chunk_data


# ====================================
#       SEND MESSAGE
# ====================================
def send_message_to_user(target_user, message, peers, gui):

    new_peers = request_peer_list()
    peers.clear()
    peers.extend(new_peers)

    for p in peers:
        if p.strip() == "":
            continue

        user, ip, tcp, udp = p.split(",")
        if user == target_user:
            network.send_tcp_message(ip, tcp, message)
            gui.show_message(f"You -> {target_user}: {message}")
            return True

    gui.show_message("[ERROR] User not found.")
    return False


# ====================================
#         SEND FILE (UDP)
# ====================================
def send_file_to_user(target_user, filepath, peers, gui):

    new_peers = request_peer_list()
    peers.clear()
    peers.extend(new_peers)

    filename = os.path.basename(filepath)

    for p in peers:
        if p.strip() == "":
            continue

        user, ip, tcp, udp = p.split(",")
        if user == target_user:

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            gui.show_message(f"[UDP] Sending '{filename}'...")

            sock.sendto(f"FILENAME:{filename}".encode(), (ip, int(udp)))

            seq = 0
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break

                    packet = seq.to_bytes(4, "big") + chunk
                    sock.sendto(packet, (ip, int(udp)))
                    seq += 1

            time.sleep(0.01)
            sock.sendto(b"EOF", (ip, int(udp)))
            sock.close()

            gui.show_message("[UDP] File sent successfully.")
            return True

    gui.show_message("[ERROR] User not found (UDP).")
    return False


# ====================================
#               MAIN
# ====================================
if __name__ == "__main__":
    register()
    peers = request_peer_list()

    gui = ChatGUI(
        lambda msg: send_message_to_user("user1", msg, peers, gui),      # FIXED
        lambda filepath: send_file_to_user("user1", filepath, peers, gui)  # FIXED
    )

    tcp_thread = TCPListener(TCP_PORT, gui)
    tcp_thread.daemon = True
    tcp_thread.start()

    udp_thread = UDPListener(UDP_PORT, gui)
    udp_thread.daemon = True
    udp_thread.start()

    gui.show_message("Welcome! You are user2.")
    gui.show_message("Send message or click 'Send File'.")

    gui.run()
