import cv2
import mediapipe as mp
import pynput
from pynput.mouse import Controller, Button
# from pynput.keyboard import Key, Controller
mouse = Controller()
current_pos = mouse.position
up_value =0
print(f'Current mouse position -> {current_pos}')

mp_hands = mp.solutions.hands #pre-trained DL model for hand recognition
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=2,               # Detect both hands
    min_detection_confidence=0.7,  # Set confidence to 70%
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)  #Use laptop camera

"""
mediapipe result contains two folders:

result.multi_hand_landmarks --> a list of hands, showing the geometry. Each hand is a list of 21 landmarks (x,y,z)

result.multihandedness --> a list of hands. Each hand has a classification list. classification[0] has three data, index;score;label
"""

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    # 1. Flip and convert color for MediaPipe
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb) # hand recognition

    # 2. If hands are detected
    if results.multi_hand_landmarks: 
        h, w, _ = frame.shape  # Get frame dimensions

        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # hand_landmarks contains 21 joint points, each has a (x,y,z) coordinate
            label = results.multi_handedness[idx].classification[0].label

            # find the min/max x and y to draw a box
            x_min, y_min = w, h
            x_max, y_max = 0, 0

            for lm in hand_landmarks.landmark:
                # convert normalized coordinates (0-1) to pixel coordinates
                px, py = int(lm.x * w), int(lm.y * h)
                
                if px < x_min: x_min = px
                if py < y_min: y_min = py
                if px > x_max: x_max = px
                if py > y_max: y_max = py

            # 3. Draw the Green Box and add labels
            # add a little padding (20 pixels) so the box isn't too tight
            cv2.rectangle(frame, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)
            
            # 4. Speed control with left hand
            if label == "Left":
                fingerUP = []
                fingertips = [20,16,12,8] #index of fingertips
                knuckles = [18,14,10,6]   #index of knuckles

                # fingers
                for i in range(4):
                    if hand_landmarks.landmark[fingertips[i]].y < hand_landmarks.landmark[knuckles[i]].y:
                        fingerUP.append(1)
                    else:
                        fingerUP.append(0)
                
                # thumb
                if hand_landmarks.landmark[4].x > hand_landmarks.landmark[2].x:
                    fingerUP.append(1)
                else:
                    fingerUP.append(0)

                cv2.putText(frame, str(sum(fingerUP)), (x_max, y_min - 20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255, 255, 255),2)
                cv2.putText(frame, "L", (x_min - 20, y_min - 20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255, 255, 255),2)

                up_value = sum(fingerUP)

            # 5. navigate with right hand
            if label == "Right":
                wrist_x = hand_landmarks.landmark[9].x
                middle_x = hand_landmarks.landmark[0].x

                # calculate the x difference of middle finger and wrist
                diff = hand_landmarks.landmark[9].x - hand_landmarks.landmark[0].x
                if diff > 0.05: 
                    
                    navigation = "right"
                    mouse.move(1,0)
                elif diff < -0.05: 
                    navigation = "left"
                    mouse.move(-1,0)
                else: 
                    navigation = "straight"
                    mouse.move(0,up_value)

                cv2.putText(frame, navigation, (x_max, y_min - 20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255, 255, 255),2)
                cv2.putText(frame, "R", (x_min - 20, y_min - 20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255, 255, 255),2)

            
    cv2.imshow('Steer Mode', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()