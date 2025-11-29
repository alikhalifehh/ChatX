import tkinter as tk
from tkinter import scrolledtext, filedialog
import os
import webbrowser
from datetime import datetime

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show(self, x, y):
        if self.tip_window:
            return

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+20}")

        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=4,
            pady=2,
            font=("Segoe UI", 9)
        )
        label.pack()

    def hide(self):
        tw = self.tip_window
        if tw:
            tw.destroy()
        self.tip_window = None

class ChatGUI:
    def __init__(self, my_username, peer_usernames, send_message_callback, send_file_callback):
        self.my_username = my_username
        self.peer_usernames = peer_usernames
        self.send_message_callback = send_message_callback
        self.send_file_callback = send_file_callback

        self.root = tk.Tk()
        self.root.title("Toozbitat")

        # Messages window
        self.messages = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word", width=60, height=20
        )
        self.messages.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # ---- TARGET USER DROPDOWN ----
        tk.Label(self.root, text="Send to:").grid(row=1, column=0, sticky="w", padx=10)

        self.target_var = tk.StringVar()

        # If no peers exist, insert placeholder
        if len(peer_usernames) == 0:
            self.peer_usernames = ["(no peers online)"]
            self.target_var.set("(no peers online)")
            no_peers = True
        else:
            self.target_var.set(peer_usernames[0])
            no_peers = False

        # Always create the dropdown with AT LEAST ONE value
        self.target_menu = tk.OptionMenu(self.root, self.target_var, *self.peer_usernames)
        self.target_menu.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        # ---- MESSAGE ENTRY ----
        self.entry = tk.Entry(self.root, width=45)
        self.entry.grid(row=2, column=0, padx=10, pady=10, sticky="we")
        self.entry.bind("<Return>", self._on_send)

        # Buttons
        self.send_button = tk.Button(self.root, text="Send", command=self._on_send)
        self.send_button.grid(row=2, column=1, padx=5, pady=10)

        self.file_button = tk.Button(self.root, text="Send File", command=self._on_send_file)
        self.file_button.grid(row=2, column=2, padx=5, pady=10)

        # Disable sending if no peers
        if no_peers:
            self.send_button.config(state="disabled")
            self.file_button.config(state="disabled")

        self.root.grid_columnconfigure(0, weight=1)

    # ---------------------- PUBLIC METHODS ----------------------

    def show_message(self, text: str):
        timestamp = datetime.now().strftime("%H:%M")
        line = f"[{timestamp}] {text}"

        self.messages.config(state="normal")
        self.messages.insert(tk.END, line + "\n")
        self.messages.see(tk.END)
        self.messages.config(state="disabled")

    def run(self):
        self.root.mainloop()

    # ---------------------- CLICKABLE FILE SUPPORT ----------------------

    def add_clickable_file(self, filepath):
        filename = os.path.basename(filepath)

        self.messages.config(state="normal")

        safe_id = abs(hash(filepath))
        tagname = f"file_{safe_id}"

        self.messages.insert(tk.END, f"[FILE] {filename}\n", tagname)

        self.messages.tag_config(tagname, foreground="blue", underline=1)

        # TOOLTIP INSTANCE
        tooltip = Tooltip(self.messages, "Click to open this file")

        # Hover bindings
        self.messages.tag_bind(
            tagname, "<Enter>",
            lambda e: tooltip.show(e.x_root, e.y_root)
        )
        self.messages.tag_bind(
            tagname, "<Leave>",
            lambda e: tooltip.hide()
        )

        # Click binding
        self.messages.tag_bind(
            tagname, "<Button-1>",
            lambda e, fn=filepath: self.open_file(fn)
        )

        self.messages.config(state="disabled")
        self.messages.see(tk.END)

    def open_file(self, filepath):
        try:
            os.startfile(filepath)  # Windows
        except:
            try:
                webbrowser.open(filepath)
            except:
                print(f"Could not open file: {filepath}")

    # ---------------------- INTERNAL EVENTS ----------------------

    def _on_send(self, event=None):
        msg = self.entry.get().strip()
        target = self.target_var.get().strip()

        if not msg or not target or target.startswith("("):
            return

        self.send_message_callback(target, msg)
        self.entry.delete(0, tk.END)

    def _on_send_file(self):
        target = self.target_var.get().strip()

        if not target or target.startswith("("):
            return

        filepath = filedialog.askopenfilename()
        if filepath:
            self.send_file_callback(target, filepath)
