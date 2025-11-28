import socket
import os
import time


# =============================
#            TCP
# =============================

def send_tcp_message(ip, tcp_port, sender_username, message):
    """
    Send a TCP message in format:
      SEND|sender|message
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(tcp_port)))
        packet = f"SEND|{sender_username}|{message}".encode()
        s.send(packet)
        s.close()
        print(f"[SENT] TCP message to {ip}:{tcp_port}")
        return True
    except Exception as e:
        print("[ERROR] Could not send TCP message:", e)
        return False


def start_tcp_listener(tcp_port, host="0.0.0.0", backlog=5):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host, int(tcp_port)))
    listener.listen(backlog)
    return listener


def recv_tcp_message(listener):
    conn, addr = listener.accept()
    data = conn.recv(4096)
    conn.close()
    try:
        text = data.decode()
    except:
        text = data.decode(errors="replace")
    return addr, text


# =============================
#            UDP
# =============================

def start_udp_listener(udp_port, host="0.0.0.0"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, int(udp_port)))
    return sock


def receive_udp_packet(sock, bufsize=65535):
    return sock.recvfrom(bufsize)


def send_udp_file(ip, udp_port, filepath, chunk_size=4096, delay=0.01, on_status=None):
    """
    Send a file over UDP using:
      FILENAME:<name>
      [4 bytes seq][chunk]
      EOF
    """
    if not os.path.isfile(filepath):
        if on_status:
            on_status("[UDP] File not found.")
        return False

    filename = os.path.basename(filepath)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if on_status:
            on_status(f"[UDP] Sending '{filename}'...")

        sock.sendto(f"FILENAME:{filename}".encode(), (ip, int(udp_port)))

        seq = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                packet = seq.to_bytes(4, "big") + chunk
                sock.sendto(packet, (ip, int(udp_port)))
                seq += 1

        time.sleep(delay)
        sock.sendto(b"EOF", (ip, int(udp_port)))
        sock.close()

        if on_status:
            on_status("[UDP] File sent successfully.")
        return True

    except Exception as e:
        if on_status:
            on_status(f"[ERROR] UDP send failed: {e}")
        return False
