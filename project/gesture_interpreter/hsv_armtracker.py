import cv2
import numpy as np

cap = cv2.VideoCapture("testvideoswim.mp4")

# Typical Skin Color Range (HSV)
# Adjust LOWER_SKIN[2] (Value/Brightness) if the room is dark
LOWER_SKIN = np.array([0, 30, 60], dtype=np.uint8)
UPPER_SKIN = np.array([20, 150, 255], dtype=np.uint8)

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. Pre-process: Blur to reduce noise from water/light
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Create Skin Mask
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)

    # 3. Clean Mask: Remove small dots and join the arm together
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=3)

    # 4. Find the Arm (Largest Contour)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Get the biggest blob (the arm)
        arm_cnt = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(arm_cnt) > 500: # Ignore tiny noise
            # Draw the arm outline
            cv2.drawContours(frame, [arm_cnt], -1, (0, 255, 0), 2)

            # --- GEOMETRY LOGIC FOR ELBOW ---
            # In a forehead view, the "Hand" is usually the point with the 
            # smallest Y (top) and the "Elbow" is the point with largest Y (bottom).
            extTop = tuple(arm_cnt[arm_cnt[:, :, 1].argmin()][0])
            extBot = tuple(arm_cnt[arm_cnt[:, :, 1].argmax()][0])

            # Draw Hand/Wrist (Top) and Elbow (Bottom)
            cv2.circle(frame, extTop, 8, (255, 0, 0), -1) # Blue = Hand
            cv2.circle(frame, extBot, 8, (0, 0, 255), -1) # Red = Elbow
            
            # Draw Forearm Vector
            cv2.line(frame, extTop, extBot, (255, 255, 0), 2)

            # Calculate Forearm Angle (relative to vertical)
            dx = extBot[0] - extTop[0]
            dy = extBot[1] - extTop[1]
            angle = np.degrees(np.arctan2(dx, dy))
            cv2.putText(frame, f"Angle: {int(angle)}deg", (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('HSV Arm Detection', frame)
    cv2.imshow('Mask (Binary)', mask) # Debugging window

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
