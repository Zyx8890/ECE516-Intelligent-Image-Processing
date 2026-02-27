import cv2 
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# This is an example made using Google's Mediapipe model, specifically HandLandmarker.
# Refer to https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python#video_2 for more info

# To switch to livestream mode, you'll have to use custom timestamps.


# NOTE: change this to your absolute path for the model
model_path = r"C:/Users/varun/Documents/Masters year 1 files/ECE 516/ECE516-Intelligent-Image-Processing/project/gesture_interpreter/hand_landmarker.task"# set up hand detection model
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    min_hand_presence_confidence=0.5 )

# >>>>>>>>>>>>>>>REPLACE WITH YOUR CAM IP IF YOU DON"T HAVE AN ESP32
ESP32_IP = "10.47.224.1"   

# path = f"http://{ESP32_IP}/stream"

# NOTE: change this to your absolute path for the video
path = r"C:/Users/varun/Documents/Masters year 1 files/ECE 516/ECE516-Intelligent-Image-Processing/project/gesture_interpreter/testvideoswim.mp4"


# >>>>>> If using a pre-recorded video, use cv2 to open that video and replace while
#        true to open new frame each loop
cap = cv2.VideoCapture(path)

if not cap.isOpened():
    print("Error: Could not access video. Check the path!")

with HandLandmarker.create_from_options(options) as landmarker:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error getting frame, retrying")
            continue
        # pass video frame to model
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format = mp.ImageFormat.SRGB, data = img)
        
        # gather hand location from model
        hand_landmarker_result = landmarker.detect_for_video(mp_img, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
        
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # show detected hand
        for landmarks in hand_landmarker_result.hand_landmarks:
                for landmark in landmarks:
                    # Convert normalized coordinates to pixel coordinates
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Swimming Analysis', frame)

        # calculate stroke

        # exit demo
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()