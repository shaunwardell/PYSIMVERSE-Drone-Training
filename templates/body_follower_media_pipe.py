
import mediapipe as mp

# Display our MediaPipe version
print("MediaPipe version:", mp.__version__)

# Access MediaPipe's computer vision tools
vision = mp.tasks.vision

# Get the body pose detector class
PoseLandmarker = vision.PoseLandmarker

# Confirm the detector is available
print("Body pose detector is available!")

# Explain our future goals
print("Next goal: Detect body landmarks.")
print("Future goal: Track a person's position.")
print("Final goal: Use body position to guide drone movement.")
