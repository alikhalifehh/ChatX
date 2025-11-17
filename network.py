import socket

def send_tcp_message(ip, tcp_port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(tcp_port)))
        s.send(message.encode())
        s.close()
        print(f"[SENT] Message sent to {ip}:{tcp_port}")
    except Exception as e:
        print("[ERROR] Could not send TCP message:", e)
