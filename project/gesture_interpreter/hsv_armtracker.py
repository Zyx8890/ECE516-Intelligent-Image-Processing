import cv2
import numpy as np

cap = cv2.VideoCapture("testvideoswim.mp4")

# Typical Skin Color Range (HSV)
# Adjust LOWER_SKIN[2] (Value/Brightness) if the room is dark
# Lower_skin is the floor range while upper_skin is the ceiling range. Anything in between is considered skin.
# H, S and V values can be adjusted based on lighting conditions and skin tones and they are 3 different channels of the HSV color space. H (Hue) represents the color type, S (Saturation) represents the intensity of the color, and V (Value) represents the brightness of the color.
LOWER_SKIN = np.array([0, 50, 80], dtype=np.uint8)
UPPER_SKIN = np.array([20, 150, 255], dtype=np.uint8)

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. Pre-process: Blur to reduce noise from water/light
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Create Skin Mask (output is binary: white=skin, black=non-skin)
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)

    # Subtract green foliage (trees) and low-saturation gray/brown (buildings, bark, sky)
    # These colors overlap with skin in hue but differ in saturation/value
    green_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([85, 255, 200]))
    gray_mask  = cv2.inRange(hsv, np.array([0,  0,  40]), np.array([180, 49, 220]))
    exclusion  = cv2.bitwise_or(green_mask, gray_mask)
    mask = cv2.bitwise_and(mask, cv2.bitwise_not(exclusion))

    # 3. Clean Mask: Remove small dots and join the arm
    # Erosion removes small white noise, while dilation enlarges the remaining white areas (the arm) to make it more solid
    # Dilation would grow the arm region back after erosion while ensuring that the small noise is removed completely. The number of iterations can be adjusted based on the quality of the video and the amount of noise present.
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=3)

    # 4. Find the Arm (Largest Contour)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame_h, frame_w = frame.shape[:2]

    def is_arm_candidate(cnt):
        area = cv2.contourArea(cnt)
        if area < 500:
            return False
        x, y, bw, bh = cv2.boundingRect(cnt)
        # Reject blobs spanning more than 40% of frame width (treeline/horizon)
        if bw > frame_w * 0.4:
            return False
        # Reject blobs with very low solidity (fragmented tree patches vs solid arm)
        hull_area = cv2.contourArea(cv2.convexHull(cnt))
        solidity = area / (hull_area + 1e-5)
        if solidity < 0.4:
            return False
        return True

    candidates = [c for c in contours if is_arm_candidate(c)]

    if candidates:
        arm_cnt = max(candidates, key=cv2.contourArea)

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
