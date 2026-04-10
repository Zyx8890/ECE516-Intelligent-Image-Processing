from pathlib import Path
import tkinter as tk
import socket
import threading
import time

# --- Configuration ---
DEFAULT_IP = "127.0.0.1"
PORT = 5005
INTERVAL = 0.1  # Seconds between packets

class RemoteController:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Controller")
        
        # State management
        self.current_command = "FORWARD"
        self.target_ip = DEFAULT_IP
        self.running = True

        # Networking setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # --- GUI Elements ---
        tk.Label(root, text="Target IP:").grid(row=0, column=0)
        self.ip_entry = tk.Entry(root)
        self.ip_entry.insert(0, DEFAULT_IP)
        self.ip_entry.grid(row=0, column=1, columnspan=2)

        # Buttons
        self.btn_left = tk.Button(root, text="LEFT", width=10, height=3)
        self.btn_fwd = tk.Button(root, text="FORWARD", width=10, height=3)
        self.btn_right = tk.Button(root, text="RIGHT", width=10, height=3)

        self.btn_left.grid(row=2, column=0)
        self.btn_fwd.grid(row=1, column=1)
        self.btn_right.grid(row=2, column=2)

        # Bindings (Press and Release)
        self.btn_fwd.bind('<ButtonPress-1>', lambda e: self.set_cmd("FORWARD"))
        self.btn_fwd.bind('<ButtonRelease-1>', lambda e: self.set_cmd("STOP"))
        
        self.btn_left.bind('<ButtonPress-1>', lambda e: self.set_cmd("LEFT"))
        self.btn_left.bind('<ButtonRelease-1>', lambda e: self.set_cmd("STOP"))
        
        self.btn_right.bind('<ButtonPress-1>', lambda e: self.set_cmd("RIGHT"))
        self.btn_right.bind('<ButtonRelease-1>', lambda e: self.set_cmd("STOP"))

        # Start the background sender thread
        self.thread = threading.Thread(target=self.send_loop, daemon=True)
        self.thread.start()

    def set_cmd(self, cmd):
        self.current_command = cmd

    def send_loop(self):
        """Continuously sends the current command over UDP."""
        while self.running:
            self.target_ip = self.ip_entry.get()
            try:
                self.sock.sendto(self.current_command.encode(), (self.target_ip, PORT))
            except Exception as e:
                print(f"Error sending: {e}")
            time.sleep(INTERVAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteController(root)
    root.mainloop()