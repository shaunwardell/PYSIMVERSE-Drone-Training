
import mediapipe as mp

# Check the installed MediaPipe version
print("MediaPipe version:", mp.__version__)

# Access MediaPipe's computer vision tools
vision = mp.tasks.vision

# Get the hand landmark detector class
HandLandmarker = vision.HandLandmarker

# Confirm the detector is available
print("Hand landmark detector is available!")

# Explain what our future program will do
print("Next goal: Detect 21 landmarks on a hand.")
print("Future goal: Convert hand gestures into drone commands.")
