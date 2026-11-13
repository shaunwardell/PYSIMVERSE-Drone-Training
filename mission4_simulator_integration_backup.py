# Mission 4: Body Follower Simulator Integration
# PYSIMVERSE Drone Training

import time
import cv2
import mediapipe as mp
from pysimverse import Drone

# SAFETY LOCK: Keep all drone movement commands disabled
DRONE_CONTROL_ENABLED = False
# Allow simulator camera access separately from movement commands
SIMULATOR_CAMERA_ENABLED = False

# Check whether simulator camera access is enabled
if SIMULATOR_CAMERA_ENABLED:
    # Create the PYSIMVERSE drone controller
    drone = Drone()

    try:
        # Connect to the PYSIMVERSE simulator
        drone.connect()

        # Activate the simulator camera stream
        drone.streamon()
        # Track the previous frame timestamp
        last_frame_timestamp_ms = -1
        # Retrieve a frame from the simulator camera
        frame, is_success = drone.get_frame()

        # Verify that the simulator camera returned a valid frame
        if is_success and frame is not None:
            print("SUCCESS: Simulator camera frame received!")
            # Convert the simulator camera frame from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the RGB frame into a MediaPipe image
            mp_frame = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )
            # Generate a monotonic timestamp in milliseconds
            frame_timestamp_ms = time.monotonic_ns() // 1_000_000
            # Ensure the timestamp is greater than the previous frame
            frame_timestamp_ms = max(
                frame_timestamp_ms,
                last_frame_timestamp_ms + 1
            )
            # Save the timestamp for the next video frame
            last_frame_timestamp_ms = frame_timestamp_ms
        else:
            print("WARNING: Simulator camera frame unavailable.")

    finally:
        # Release simulator resources even if an error occurs
        drone.shutdown()
        print("Simulator shutdown completed.")
    print("Simulator camera access enabled.")
else:
    print("Simulator camera access disabled.")
# Configure MediaPipe for video processing
vision = mp.tasks.vision

PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerOptions = vision.PoseLandmarkerOptions
BaseOptions = mp.tasks.BaseOptions

# Location of our existing body detection model
model_path = "models/pose_landmarker_lite.task"

# Configure the detector for timestamped video frames
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=vision.RunningMode.VIDEO
)

print("Mission 4: Simulator Integration")
print("OpenCV version:", cv2.__version__)
print("MediaPipe version:", mp.__version__)

if not DRONE_CONTROL_ENABLED:
    print("SAFETY LOCK ACTIVE: Drone commands disabled.")
    print("MediaPipe running mode:", options.running_mode)
    # Test loading our body detector in VIDEO mode
    with PoseLandmarker.create_from_options(options) as detector:
        print("SUCCESS: VIDEO mode body detector loaded!")
        # Load a photograph as our first simulated video frame
        image = mp.Image.create_from_file("test_images/body_test.jpg")

        # Process the frame with a timestamp of 1000 milliseconds
        results = detector.detect_for_video(image, 1000)

        # Process a second simulated video frame
        second_results = detector.detect_for_video(image, 1033)

        # Check whether the second frame detected a human
        if second_results.pose_landmarks:
            print("SUCCESS: Human detected in second video frame!")
            print("Second frame landmarks:", len(second_results.pose_landmarks[0]))
            # Extract shoulder landmarks from the detected body
            body = second_results.pose_landmarks[0]
            left_shoulder = body[11]
            right_shoulder = body[12]
            # Calculate the horizontal center of the shoulders
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            # Calculate normalized shoulder width for distance estimation
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            # Display shoulder measurements for debugging
            print("Shoulder center X:", round(shoulder_center_x, 3))
            print("Shoulder width:", round(shoulder_width, 3))
            # Define horizontal boundaries for the center zone
            CENTER_LEFT = 0.40
            CENTER_RIGHT = 0.60
            # Determine whether the person is left of center
            if shoulder_center_x < CENTER_LEFT:
                horizontal_position = "LEFT"
            elif shoulder_center_x > CENTER_RIGHT:
                horizontal_position = "RIGHT"
            else:
                horizontal_position = "CENTERED"
            # Display the calculated horizontal position
            print("Horizontal position:", horizontal_position)
            # Define shoulder-width thresholds for distance estimation
            MIN_SHOULDER_WIDTH = 0.15
            MAX_SHOULDER_WIDTH = 0.30
            # Determine whether the person appears too far away
            if shoulder_width < MIN_SHOULDER_WIDTH:
                distance_status = "TOO FAR"
            elif shoulder_width > MAX_SHOULDER_WIDTH:
                distance_status = "TOO CLOSE"
            else:
                distance_status = "GOOD DISTANCE"
            # Display the calculated distance status
            print("Distance status:", distance_status)
            # Determine the simulated horizontal follower action
            if horizontal_position == "LEFT":
                horizontal_action = "MOVE LEFT"
            elif horizontal_position == "RIGHT":
                horizontal_action = "MOVE RIGHT"
            else:
                horizontal_action = "HOLD POSITION"
            # Display the simulated horizontal follower action
            print("Horizontal follower action:", horizontal_action)
            # Determine the simulated distance follower action
            if distance_status == "TOO FAR":
                distance_action = "MOVE FORWARD"
            elif distance_status == "TOO CLOSE":
                distance_action = "MOVE BACKWARD"
            else:
                distance_action = "HOLD DISTANCE"
            # Display the simulated distance follower action
            print("Distance follower action:", distance_action)

        else:
            print("No human detected in second video frame.")
            # Select safe simulated actions when the target is lost
            horizontal_action = "STOP/HOVER"
            distance_action = "STOP/HOVER"
            # Display the simulated target-loss safety action
            print("SAFETY: Target lost. STOP/HOVER selected.")

        # Check whether a human body was detected
        if results.pose_landmarks:
            print("SUCCESS: Human detected in VIDEO mode!")
            print("Body landmarks:", len(results.pose_landmarks[0]))
        else:
            print("No human detected in VIDEO mode.")

    print("VIDEO mode detector closed safely.")