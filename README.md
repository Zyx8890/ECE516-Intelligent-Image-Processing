#### ECE516 Project : Gesture-controlled aquatic interface

## Intro

This project provides insight into ways of controlling a virtual or physical aquatic vessel through gesture control. 
The user wears an ESP32-Cam module on their forehead, which is used to track the swimming motions of a user. Based on the speed and direction of the user's input, a physical (or virtual) vessel can be controlled. 

Specific control interface instructions coming soon.

## Components

Project files are located inside the `project` directory and are separated into 3 parts:
1) [ESP camera stream](/project/esp_camera_stream/), used to send a video stream from the esp module to a python server
2) [Gesture Interpreter](/project/gesture_interpreter/), used to interpret a live video stream and categorize user inputs into forward, left and right
3) [game_files](/project/game_files/), that take in forward, left and right inputs and maneuver a virtual boat

## Additional Information

Code used in labs for the ECE516 course can also be found here.
Lab 1: Modifying Camera Parameters
Lab 2: Metaveillography (Observing camera feedback)
Lab 3: Sequential Wave-Imprinting Machine (SWIM)
