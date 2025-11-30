import sys
import socket
import network
import threading_utils
from gui import ChatGUI
from logger import log    # <-- NEW

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))
    return s


def register(username, tcp_port, udp_port):
    s = connect_to_server()
    msg = f"REGISTER|{username}|{tcp_port}|{udp_port}"
    s.send(msg.encode())
    reply = s.recv(1024).decode()
    print("[SERVER REPLY]", reply)

    log(f"REGISTERED User={username} TCP={tcp_port} UDP={udp_port}")

    s.close()


def request_peer_list():
    s = connect_to_server()
    s.send("REQUEST_LIST".encode())
    data = s.recv(4096).decode()
    s.close()

    log("Requested peer list from server")

    peers = []
    for p in data.split("|"):
        if p.strip():
            peers.append(p)
    return peers


def get_peer_usernames(peers, my_username):
    names = []
    for p in peers:
        user, ip, tcp, udp = p.split(",")
        if user != my_username:
            names.append(user)
    return names


def find_peer_info(peers, username):
    for p in peers:
        user, ip, tcp, udp = p.split(",")
        if user == username:
            return ip, tcp, udp
    return None


def send_message_to_user(target_user, message, peers, gui, my_username):
    peers[:] = request_peer_list()

    info = find_peer_info(peers, target_user)
    if info is None:
        gui.show_message("[ERROR] User not found.")
        log(f"[ERROR] Tried to send message to NON-EXISTING user '{target_user}'")
        return

    ip, tcp, udp = info
    ok = network.send_tcp_message(ip, tcp, my_username, message)
    if ok:
        gui.show_message(f"You → {target_user}: {message}")

        # LOG
        log(f"GUI SENT MESSAGE → {target_user}: '{message}'")


def send_file_to_user(target_user, filepath, peers, gui):
    peers[:] = request_peer_list()

    info = find_peer_info(peers, target_user)
    if info is None:
        gui.show_message("[ERROR] User not found (UDP).")
        log(f"[ERROR] Tried to send file to NON-EXISTING user '{target_user}'")
        return

    ip, tcp, udp = info

    ok = network.send_udp_file(ip, udp, filepath, on_status=gui.show_message)

    if ok:
        gui.show_message(f"[UDP] You sent a file to {target_user}.")
        gui.add_clickable_file(filepath)

        # LOG
        log(f"GUI SENT FILE → {target_user}: '{filepath}'")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <username> <tcp_port> <udp_port>")
        sys.exit(1)

    USERNAME = sys.argv[1]
    TCP_PORT = sys.argv[2]
    UDP_PORT = sys.argv[3]

    log("=== CLIENT STARTED ===")

    register(USERNAME, TCP_PORT, UDP_PORT)
    peers = request_peer_list()

    peer_names = get_peer_usernames(peers, USERNAME)

    gui = ChatGUI(
        USERNAME,
        peer_names,
        lambda target, msg: send_message_to_user(target, msg, peers, gui, USERNAME),
        lambda target, path: send_file_to_user(target, path, peers, gui)
    )

    tcp_thread = threading_utils.TCPListenerThread(TCP_PORT, gui)
    udp_thread = threading_utils.UDPListenerThread(UDP_PORT, gui)
    tcp_thread.start()
    udp_thread.start()

    log("TCP and UDP listener threads started")

    gui.show_message(f"Welcome! You are {USERNAME}.")
    if not peer_names:
        gui.show_message("No peers online yet. Restart client after others join.")

    gui.run()

    log("GUI closed — client shutting down")
