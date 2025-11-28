import threading
import os
import network


def _safe_gui_call(gui, func, *args):
    """Tkinter-safe GUI update using root.after."""
    if gui is None:
        return
    try:
        gui.root.after(0, func, *args)
    except Exception:
        func(*args)


class TCPListenerThread(threading.Thread):
    def __init__(self, tcp_port, gui):
        super().__init__(daemon=True)
        self.tcp_port = tcp_port
        self.gui = gui
        self.running = True
        self.listener = None

    def stop(self):
        self.running = False
        try:
            if self.listener:
                self.listener.close()
        except:
            pass

    def run(self):
        self.listener = network.start_tcp_listener(self.tcp_port)
        print(f"[TCP LISTENER] Listening on {self.tcp_port}")

        while self.running:
            try:
                addr, raw = network.recv_tcp_message(self.listener)

                # NEW TCP FORMAT:
                # SEND|sender_username|message
                parts = raw.split("|")

                if len(parts) >= 3 and parts[0] == "SEND":
                    sender = parts[1]
                    msg = "|".join(parts[2:])   # handles "|" inside message
                    _safe_gui_call(self.gui, self.gui.show_message, f"{sender} → {msg}")
                else:
                    # fallback for malformed packets
                    _safe_gui_call(self.gui, self.gui.show_message, raw)

            except OSError:
                break
            except Exception as e:
                print("[TCP LISTENER ERROR]", e)


class UDPListenerThread(threading.Thread):
    def __init__(self, udp_port, gui):
        super().__init__(daemon=True)
        self.udp_port = udp_port
        self.gui = gui
        self.running = True
        self.sock = None

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except:
            pass

    def run(self):
        self.sock = network.start_udp_listener(self.udp_port)
        print(f"[UDP LISTENER] Listening on {self.udp_port}")

        filename = None
        chunks = {}

        while self.running:
            try:
                data, addr = network.receive_udp_packet(self.sock)

                # START
                if data.startswith(b"FILENAME:"):
                    filename = data.split(b":", 1)[1].decode()
                    chunks = {}
                    _safe_gui_call(self.gui, self.gui.show_message, f"[UDP] Receiving '{filename}'...")
                    continue

                # END
                if b"EOF" in data:
                    if filename is None:
                        continue

                    clean = data.replace(b"EOF", b"")
                    if clean:
                        seq = max(chunks.keys()) + 1 if chunks else 0
                        chunks[seq] = clean

                    ordered = b"".join(chunks[i] for i in sorted(chunks.keys()))
                    save_name = os.path.abspath("received_" + filename)

                    with open(save_name, "wb") as f:
                        f.write(ordered)

                    _safe_gui_call(self.gui, self.gui.show_message, f"[UDP] File '{save_name}' saved.")
                    _safe_gui_call(self.gui, self.gui.add_clickable_file, save_name)

                    filename = None
                    chunks = {}
                    continue

                # NORMAL CHUNK
                if filename is not None:
                    seq = int.from_bytes(data[:4], "big")
                    chunk_data = data[4:]
                    chunks[seq] = chunk_data

            except OSError:
                break
            except Exception as e:
                print("[UDP LISTENER ERROR]", e)
