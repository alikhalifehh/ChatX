import socket
import os
import time
from logger import log   # logging

# =============================
#       BASIC ENCRYPTION
# =============================

SECRET_KEY = b"my_simple_key"   # shared XOR key


def xor_crypt(data: bytes) -> bytes:
    """
    Simple XOR encryption/decryption.
    Same function for encrypt + decrypt.
    """
    key = SECRET_KEY
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


# =============================
#            TCP
# =============================

def send_tcp_message(ip, tcp_port, sender_username, message):
    """
    Send a TCP message in format:
        SEND|sender|message
    Entire packet is encrypted before sending.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(tcp_port)))

        # Plain text payload
        plaintext = f"SEND|{sender_username}|{message}".encode()

        # Encrypt it
        encrypted = xor_crypt(plaintext)

        # >>> DEBUG: SHOW ENCRYPTED TCP BYTES <<<
        print("PLAINTEXT:", plaintext)
        print("ENCRYPTED TCP DATA:", encrypted)
        print("----------------------------------------")

        # Send encrypted data
        s.send(encrypted)
        s.close()

        log(f"TCP SENT → {ip}:{tcp_port} | From={sender_username} | Msg='{message}'")
        return True

    except Exception as e:
        print("[ERROR] Could not send TCP message:", e)
        log(f"[ERROR] TCP SEND FAILED to {ip}:{tcp_port}: {e}")
        return False


def start_tcp_listener(tcp_port, host="0.0.0.0", backlog=5):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host, int(tcp_port)))
    listener.listen(backlog)
    return listener


def recv_tcp_message(listener):
    """
    Receive encrypted TCP data, decrypt it, return plaintext text.
    """
    conn, addr = listener.accept()
    enc_data = conn.recv(4096)
    conn.close()

    try:
        decrypted = xor_crypt(enc_data)
        try:
            text = decrypted.decode()
        except:
            text = decrypted.decode(errors="replace")

    except Exception as e:
        log(f"[ERROR] TCP DECRYPT FAILED from {addr}: {e}")
        text = ""

    log(f"TCP RECEIVED ← from {addr}: {text}")
    return addr, text


# =============================
#            UDP
# =============================

def start_udp_listener(udp_port, host="0.0.0.0"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, int(udp_port)))
    return sock


def receive_udp_packet(sock, bufsize=65535):
    """
    Receives UDP packets.
    - "FILENAME:<name>" is plain
    - "EOF" is plain
    - chunks are encrypted: [4 bytes seq][encrypted chunk]
    """
    packet, addr = sock.recvfrom(bufsize)

    # Filename header (not encrypted)
    if packet.startswith(b"FILENAME:"):
        log(f"UDP RECEIVED FILENAME HEADER from {addr}: {packet.decode()}")
        return packet, addr

    # EOF (not encrypted)
    if packet == b"EOF":
        log(f"UDP RECEIVED EOF from {addr}")
        return packet, addr

    # Encrypted chunk
    seq_bytes = packet[:4]
    encrypted_chunk = packet[4:]

    # Decrypt chunk
    decrypted_chunk = xor_crypt(encrypted_chunk)
    new_packet = seq_bytes + decrypted_chunk

    seq = int.from_bytes(seq_bytes, "big")
    log(f"UDP RECEIVED CHUNK seq={seq} from {addr} (size={len(decrypted_chunk)})")

    return new_packet, addr


def send_udp_file(ip, udp_port, filepath, chunk_size=4096, delay=0.01, on_status=None):
    """
    Send encrypted file chunks:
    - Header: FILENAME:<name> (plain)
    - Data: [4 bytes seq][xor encrypted chunk]
    - EOF (plain)
    """
    if not os.path.isfile(filepath):
        if on_status:
            on_status("[UDP] File not found.")
        log(f"[ERROR] UDP SEND FAILED: File not found '{filepath}'")
        return False

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if on_status:
            on_status(f"[UDP] Sending '{filename}'...")

        log(f"UDP SEND START → {ip}:{udp_port} | File='{filename}' ({filesize} bytes)")

        # Send filename header (plain)
        sock.sendto(f"FILENAME:{filename}".encode(), (ip, int(udp_port)))

        seq = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                # Encrypt the chunk
                encrypted_chunk = xor_crypt(chunk)

                # >>> DEBUG: SHOW ENCRYPTED FILE BYTES <<<
                print(f"ENCRYPTED UDP CHUNK seq={seq}: {encrypted_chunk[:50]} ...")

                # Build packet
                packet = seq.to_bytes(4, "big") + encrypted_chunk
                sock.sendto(packet, (ip, int(udp_port)))

                log(f"UDP SENT CHUNK seq={seq} to {ip}:{udp_port} (size={len(chunk)})")
                seq += 1

        time.sleep(delay)
        sock.sendto(b"EOF", (ip, int(udp_port)))
        sock.close()

        if on_status:
            on_status("[UDP] File sent successfully.")

        log(f"UDP SEND COMPLETE | File='{filename}' ({filesize} bytes)")
        return True

    except Exception as e:
        if on_status:
            on_status(f"[ERROR] UDP send failed: {e}")
        log(f"[ERROR] UDP SEND FAILED during file '{filename}': {e}")
        return False
