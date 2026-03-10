from pathlib import Path

import cv2
import numpy as np
VIDEO_PATH = str(Path(__file__).resolve().parent / "alexmove.mp4")

cap = cv2.VideoCapture(VIDEO_PATH)

# --- CONFIGURATION ---
LOWER_SKIN = np.array([0, 80, 80], dtype=np.uint8)
UPPER_SKIN = np.array([20, 150, 255], dtype=np.uint8)
MERGE_DISTANCE = 20  # Distance in pixels to merge a small blob into a large arm

while True:
    ret, frame = cap.read()
    if not ret: break
    h, w = frame.shape[:2]

    # 1. MASKING (Standard)
    blurred = cv2.GaussianBlur(frame, (7, 7), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_SKIN, UPPER_SKIN)
    
    # 2. INITIAL CONTOUR FILTRATION
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Separate blobs by size
    seeds = [] # Potential Arms
    scraps = [] # Small blobs to potentially merge
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100: continue # Eliminate tiny noise entirely
        
        M = cv2.moments(cnt)
        if M["m00"] == 0: continue
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
        if area > 1000:
            seeds.append({"cnt": cnt, "center": center, "area": area})
        else:
            scraps.append({"cnt": cnt, "center": center})

    # 3. LIMIT TO TOP 2 SEEDS
    seeds = sorted(seeds, key=lambda x: x['area'], reverse=True)[:2]

    # 4. MERGE LOGIC
    final_arms = []
    for seed in seeds:
        # Start the arm with the seed's points
        arm_points = seed["cnt"]
        
        # Check all scraps to see if they are close to this specific seed
        for scrap in scraps[:]: # Iterate over a copy so we can remove merged ones
            dist = np.linalg.norm(np.array(seed["center"]) - np.array(scrap["center"]))
            
            if dist < MERGE_DISTANCE:
                # Merge the points of the small blob into the arm
                arm_points = np.vstack((arm_points, scrap["cnt"]))
        
        # Create a new solid shape around the merged parts
        merged_hull = cv2.convexHull(arm_points)
        final_arms.append(merged_hull)

    # 5. DRAWING
    for i, arm in enumerate(final_arms):
        color = (0, 255, 0) if i == 0 else (255, 255, 0) # Green for Arm 1, Cyan for Arm 2
        cv2.drawContours(frame, [arm], -1, color, 2)
        
        # Geometry for Forearm line
        extTop = tuple(arm[arm[:, :, 1].argmin()][0])
        extBot = tuple(arm[arm[:, :, 1].argmax()][0])
        cv2.line(frame, extTop, extBot, (0, 0, 255), 2)
        cv2.putText(frame, f"Arm {i+1}", (extTop[0], extTop[1]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('Dual Arm Merge Tracker', frame)
    if cv2.waitKey(30) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()