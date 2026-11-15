# PYSIMVERSE Drone Training

## Project Overview

A Python-based drone simulation and computer vision training project focused on developing software that interprets visual information and makes autonomous flight decisions.

This project explores drone control, camera integration, hand gesture recognition, human body tracking, jump detection, and autonomous line following using the PYSIMVERSE drone simulator.

The project was developed through five training missions, progressing from basic drone control to autonomous navigation using computer vision.

**Project Status: Completed | November 15, 2026**

## Technologies Used

- Python
- PyCharm
- OpenCV
- MediaPipe
- cvzone
- NumPy
- PYSIMVERSE Drone Simulator
- Git and GitHub

## Project Missions

### Mission 1: Drone Fundamentals

Explored drone connection and basic flight-control functionality in the simulator.

- Established drone connections.
- Practiced basic flight commands.
- Explored simulator navigation and drone movement.

### Mission 2: Camera Integration

Practiced accessing camera frames through the PYSIMVERSE drone API.

- Established camera streaming.
- Retrieved and displayed drone camera frames.
- Practiced keyboard-based drone controls.

### Mission 3: Hand Gesture Recognition

Developed a computer vision prototype using MediaPipe to detect hand landmarks and interpret gestures.

- Detected 21 hand landmarks.
- Tested open-hand and fist recognition.
- Generated simulated takeoff and landing decisions.
- Kept actual gesture-controlled flight disabled during prototype testing.

### Mission 4: Human Body Tracking and Jump Detection

Developed body-following and jump-detection prototypes using OpenCV and MediaPipe Pose Landmarker.

Features include:

- Detection of 33 human body landmarks.
- Shoulder-position analysis for left, right, and centered tracking.
- Shoulder-width analysis for distance decisions.
- Simulated movement recommendations.
- Target-loss detection with a simulated STOP/HOVER response.
- Webcam-based human tracking.
- Jump-detection development and testing.

### Mission 5: Autonomous Line Following

Developed an autonomous drone navigation program capable of following a red line inside the PYSIMVERSE simulator.

The system uses computer vision to detect the red path, estimate its direction, and adjust simulated drone movement.

Features include:

- Real-time drone camera processing.
- Red-line detection using HSV color filtering.
- OpenCV-based image processing.
- Path-position and direction estimation.
- Automatic steering corrections.
- Adaptive forward speeds for straight sections and curves.
- Autonomous navigation through curved sections.
- Safe landing and simulator shutdown procedures.

**Mission 5 Achievement:**

- Successfully completed the autonomous line-following course.
- Achieved a best recorded completion time of **11.19 seconds**.
- Earned **three diamonds** in the simulator.
- Improved completion time from an initial 51.39 seconds to 11.19 seconds.
- Reduced completion time by approximately **78.2%** through iterative speed tuning.

## Testing and Results

### Mission 4 Testing

- 14 offline direction and distance decision tests.
- Successful human detection using still images.
- Successful MediaPipe VIDEO-mode detection.
- Webcam tracking tests with 10-frame execution limits.
- Successful LEFT, RIGHT, and CENTERED tracking tests.
- Successful target-loss safety testing.

### Mission 5 Testing

- Verified drone connection, takeoff, landing, and camera streaming.
- Tested yaw rotation behavior.
- Calibrated HSV values for red-line detection.
- Developed and tested autonomous steering logic.
- Adjusted forward speeds to improve navigation performance.
- Successfully completed the simulator course multiple times.
- Achieved a best completion time of 11.19 seconds with three diamonds.

**Best-performing configuration:**

```python
FORWARD_STRAIGHT = 32
FORWARD_CURVE = 8
MAX_YAW = 12
```

Performance may vary between simulator runs.

## Safety

This project was developed for educational purposes in a simulated environment.

Gesture recognition and body-following prototypes use simulated decisions and safety controls rather than unrestricted physical drone commands.

Mission 5 uses autonomous movement commands within the PYSIMVERSE simulator.

Safety-related functionality includes:

- Target-loss detection.
- STOP/HOVER decisions.
- Controlled simulator landing.
- Drone shutdown procedures.

The project has not been validated for autonomous operation with physical drones.

## Current Status

**All five training missions have been completed.**

- Mission 1: Drone Fundamentals — Complete
- Mission 2: Camera Integration — Complete
- Mission 3: Hand Gesture Recognition — Complete
- Mission 4: Human Body Tracking and Jump Detection — Complete
- Mission 5: Autonomous Line Following — Complete

**Course Completion:** November 15, 2026

Successfully completed the SkillSphere course:

*Learn AI Drone Programming in a Simulator (Pysimverse) with Python | 2026*

Awarded a certificate of completion.

Mission 4 webcam tracking is functional. Full live body-following integration with simulator movement commands remains a future development opportunity.

## Future Development

- Improve live human tracking.
- Integrate body-following decisions with simulator movement commands.
- Expand gesture recognition.
- Improve autonomous tracking stability.
- Explore additional computer vision and robotics applications.
- Experiment with more advanced autonomous navigation algorithms.

## Author

**Sandra Epnett**

Computer programming and IT student at DeVry University.

Interested in artificial intelligence, computer vision, software development, robotics simulation, and autonomous systems.