import cv2

ESP32_IP = ""   
url = f"http://{ESP32_IP}:81/stream"

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
