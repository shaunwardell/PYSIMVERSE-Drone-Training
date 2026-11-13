
import cv2
import time
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import PoseLandmarker


# Mission 4: Webcam Body Follower
# Simulation decisions only. No drone movement commands.

MAX_WEBCAM_FRAMES = 10
webcam_frame_count = 0
last_frame_timestamp_ms = -1


# Configure the MediaPipe body detection model
base_options = python.BaseOptions(
    model_asset_path="models/pose_landmarker_lite.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)

# Initialize the MediaPipe body detector
detector = PoseLandmarker.create_from_options(options)
print("SUCCESS: Webcam body detector initialized!")

# Open the laptop webcam
camera = cv2.VideoCapture(0)

try:
    if camera.isOpened():
        print("SUCCESS: Python connected to the laptop webcam!")

        # Process up to 10 webcam frames
        while webcam_frame_count < MAX_WEBCAM_FRAMES:

            success, frame = camera.read()

            # Handle webcam capture failure
            if not success or frame is None:
                print("WARNING: Unable to capture webcam frame.")
                print("SIMULATED SAFETY DECISION: STOP/HOVER")
                break

            # Count successfully captured frames
            webcam_frame_count += 1

            print()
            print("================================")
            print("Processing webcam frame:", webcam_frame_count)
            print("================================")

            print("SUCCESS: Webcam frame captured!")
            print("Frame dimensions:", frame.shape)

            # Convert BGR webcam frame to RGB
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # Convert to MediaPipe image
            mp_frame = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Generate an increasing timestamp
            frame_timestamp_ms = time.monotonic_ns() // 1_000_000

            frame_timestamp_ms = max(
                frame_timestamp_ms,
                last_frame_timestamp_ms + 1
            )

            last_frame_timestamp_ms = frame_timestamp_ms

            # Detect body landmarks
            results = detector.detect_for_video(
                mp_frame,
                frame_timestamp_ms
            )

            # Check whether a person was detected
            if results.pose_landmarks:

                print("SUCCESS: Human detected through laptop webcam!")

                webcam_body = results.pose_landmarks[0]

                print("Body landmarks:", len(webcam_body))

                # Identify shoulders
                webcam_left_shoulder = webcam_body[11]
                webcam_right_shoulder = webcam_body[12]

                # Calculate horizontal shoulder center
                webcam_shoulder_center_x = (
                    webcam_left_shoulder.x
                    + webcam_right_shoulder.x
                ) / 2

                # Calculate apparent shoulder width
                webcam_shoulder_width = abs(
                    webcam_left_shoulder.x
                    - webcam_right_shoulder.x
                )

                print(
                    "Webcam shoulder center X:",
                    round(webcam_shoulder_center_x, 3)
                )

                print(
                    "Webcam shoulder width:",
                    round(webcam_shoulder_width, 3)
                )

                # Determine horizontal position
                if webcam_shoulder_center_x < 0.40:
                    webcam_horizontal_position = "LEFT"

                elif webcam_shoulder_center_x > 0.60:
                    webcam_horizontal_position = "RIGHT"

                else:
                    webcam_horizontal_position = "CENTERED"

                # Select simulated horizontal action
                if webcam_horizontal_position == "LEFT":
                    webcam_horizontal_action = "MOVE LEFT"

                elif webcam_horizontal_position == "RIGHT":
                    webcam_horizontal_action = "MOVE RIGHT"

                else:
                    webcam_horizontal_action = "HOLD POSITION"

                print(
                    "Webcam horizontal position:",
                    webcam_horizontal_position
                )

                print(
                    "Webcam horizontal action:",
                    webcam_horizontal_action
                )

                # Determine apparent distance
                if webcam_shoulder_width < 0.15:
                    webcam_distance_status = "TOO FAR"

                elif webcam_shoulder_width > 0.30:
                    webcam_distance_status = "TOO CLOSE"

                else:
                    webcam_distance_status = "GOOD DISTANCE"

                # Select simulated distance action
                if webcam_distance_status == "TOO FAR":
                    webcam_distance_action = "MOVE FORWARD"

                elif webcam_distance_status == "TOO CLOSE":
                    webcam_distance_action = "MOVE BACKWARD"

                else:
                    webcam_distance_action = "HOLD DISTANCE"

                # Display distance tracking decisions
                print(
                    "Webcam distance status:",
                    webcam_distance_status
                )

                print(
                    "Webcam distance action:",
                    webcam_distance_action
                )

            else:
                print("WARNING: No human detected in webcam frame.")
                print("SIMULATED SAFETY DECISION: STOP/HOVER")

            # Small delay to keep testing lightweight
            time.sleep(0.2)

    else:
        print("ERROR: Python could not access the webcam.")

finally:
    # Always release camera and detector resources
    camera.release()
    detector.close()

    print()
    print("Webcam test completed.")
    print("Total frames processed:", webcam_frame_count)
