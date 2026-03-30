import socket
import time

# Configuration
UDP_IP = "192.168.1.XX" # Put your ESP8266 IP here
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_cmd(command):
    print(f"Sending: {command}")
    sock.sendto(command.encode(), (UDP_IP, UDP_PORT))

# Example Sequence
try:
    send_cmd("FORWARD")
    time.sleep(2)
    send_cmd("LEFT")
    time.sleep(1)
    send_cmd("STOP")
except KeyboardInterrupt:
    send_cmd("STOP")
