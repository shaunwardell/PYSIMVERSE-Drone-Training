
# PYSIMVERSE Drone Training

## Project Overview

A Python-based drone simulation and computer vision training project focused on learning how software can interpret visual information and make simulated flight decisions.

The project explores drone control, camera integration, hand gesture recognition, and human body tracking using the PYSIMVERSE simulator.

## Technologies Used

- Python
- PyCharm
- OpenCV
- MediaPipe
- PYSIMVERSE Drone Simulator
- Git and GitHub

## Project Missions

### Mission 1: Drone Fundamentals
Explored drone connection and basic flight-control functionality in the simulator.

### Mission 2: Camera Integration
Practiced accessing camera frames through the PYSIMVERSE drone API.

### Mission 3: Hand Gesture Recognition
Developed a computer vision prototype using MediaPipe to detect hand landmarks and interpret gestures.

- Detected 21 hand landmarks.
- Tested open-hand and fist recognition.
- Generated simulated takeoff and landing decisions.
- Kept actual gesture-controlled flight disabled.

### Mission 4: Human Body Tracking
Developed a body-following decision prototype using OpenCV and MediaPipe Pose Landmarker.

Features include:

- Detection of 33 human body landmarks.
- Shoulder-position analysis for left, right, and centered tracking.
- Shoulder-width analysis for distance decisions.
- Simulated movement recommendations.
- Target-loss detection with a simulated STOP/HOVER response.

## Testing and Results

Mission 4 testing included:

- 14 offline direction and distance decision tests.
- Successful human detection using still images.
- Successful MediaPipe VIDEO-mode detection.
- Webcam tracking tests with 10-frame execution limits.
- Successful LEFT, RIGHT, and CENTERED tracking tests.
- Successful target-loss safety testing.

## Safety

This project is a learning and simulation prototype.

Computer vision decisions are simulated and are not automatically translated into physical drone flight commands.

The project maintains a disabled drone-control safety flag during computer vision testing.

## Current Status

Missions 1 through 4 have been developed and tested at the prototype level.

Mission 4 webcam body tracking is functional. Full live simulator tracking and movement-command integration remain future development goals.

## Future Development

- Improve live human tracking.
- Integrate body-following decisions with simulator movement commands.
- Expand gesture recognition.
- Improve tracking stability and safety checks.
- Explore additional computer vision and robotics applications.

## Author

Sandra Epnett

Computer programming and IT student at DeVry University.
