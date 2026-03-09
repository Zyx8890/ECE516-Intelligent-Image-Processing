import serial
import cv2
import numpy as np
import time

# Use 115200 for now, we will go faster later
ser = serial.Serial('COM3', 115200, timeout=0.5) 

# Toggle DTR/RTS to reset the board
ser.setDTR(False)
time.sleep(0.5)
ser.setDTR(True)

print("Waiting for camera to initialize...")
time.sleep(2) # Give the ESP32 2 seconds to boot up

while True:
    try:
        # Check if there is ANYTHING in the buffer
        if ser.in_waiting > 0:
            # Look for the marker
            header = ser.read_until(b"START")
            
            if b"START" in header:
                # Read the size
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.isdigit():
                    size = int(line)
                    raw_data = ser.read(size)
                    
                    # Process Image
                    img_array = np.frombuffer(raw_data, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        cv2.imshow("Stream", frame)
                        cv2.waitKey(1)
        else:
            # If buffer is empty, don't just sit there—keep checking
            pass

    except Exception as e:
        print(f"Error: {e}")