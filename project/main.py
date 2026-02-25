import cv2
import numpy


ESP32_IP = "10.47.224.1"   
url = f"http://{ESP32_IP}/stream"

cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()  # ret is a Boolean (True when captured), frame is numPy array
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("ESP32-CAM", frame) 

    if cv2.waitKey(1) & 0xFF == ord('q'): # press q to quit
        break

cap.release()
cv2.destroyAllWindows()
