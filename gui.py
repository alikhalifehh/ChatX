import tkinter as tk
from tkinter import scrolledtext, filedialog
import os
import webbrowser


class ChatGUI:
    def __init__(self, send_message_callback, send_file_callback):
        """
        send_message_callback(msg: str)
        send_file_callback(filepath: str)
        """
        self.send_message_callback = send_message_callback
        self.send_file_callback = send_file_callback

        self.root = tk.Tk()
        self.root.title("ChatX")

        # Messages window
        self.messages = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word", width=60, height=20
        )
        self.messages.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Message entry
        self.entry = tk.Entry(self.root, width=50)
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="we")
        self.entry.bind("<Return>", self._on_send)

        # Send text button
        self.send_button = tk.Button(self.root, text="Send", command=self._on_send)
        self.send_button.grid(row=1, column=1, padx=5, pady=10)

        # Send File button
        self.file_button = tk.Button(self.root, text="Send File", command=self._on_send_file)
        self.file_button.grid(row=1, column=2, padx=5, pady=10)

        self.root.grid_columnconfigure(0, weight=1)

    # ---------------------- PUBLIC METHODS ----------------------

    def show_message(self, text: str):
        self.messages.config(state="normal")
        self.messages.insert(tk.END, text + "\n")
        self.messages.see(tk.END)
        self.messages.config(state="disabled")

    def run(self):
        self.root.mainloop()

    # ---------------------- CLICKABLE FILE SUPPORT ----------------------

    def add_clickable_file(self, filename):
        """
        Inserts a clickable file link into the chat window.
        """
        self.messages.config(state="normal")

        # Create unique tag for this specific filename
        tagname = f"file_{filename}"

        self.messages.insert(tk.END, f"[FILE] {filename}\n", tagname)

        self.messages.tag_config(
            tagname,
            foreground="blue",
            underline=1
        )

        # Bind click event
        self.messages.tag_bind(tagname, "<Button-1>", lambda e, fn=filename: self.open_file(fn))

        self.messages.config(state="disabled")
        self.messages.see(tk.END)

    def open_file(self, filepath):
        try:
            os.startfile(filepath)  # Windows
        except:
            try:
                webbrowser.open(filepath)  # fallback
            except:
                print(f"Could not open file: {filepath}")

    # ---------------------- INTERNAL GUI EVENTS ----------------------

    def _on_send(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            self.send_message_callback(msg)
            self.entry.delete(0, tk.END)

    def _on_send_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.send_file_callback(filepath)
