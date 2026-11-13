# Mission 4: Body Follower Simulator Integration
# PYSIMVERSE Drone Training

import time
import cv2
import mediapipe as mp
from pysimverse import Drone

# SAFETY LOCK: Keep all drone movement commands disabled
DRONE_CONTROL_ENABLED = False
# Allow simulator camera access separately from movement commands
SIMULATOR_CAMERA_ENABLED = True

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
        # Process simulator camera frames while the MediaPipe detector is active
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

                # Limit simulator tracking to five camera frames
                SIMULATOR_FRAME_LIMIT = 5

                # Process a limited number of simulator camera frames
                for frame_number in range(SIMULATOR_FRAME_LIMIT):
                    # Display the current simulator frame number
                    print("Processing simulator frame:", frame_number + 1)

                    # Retrieve a frame from the simulator camera
                    frame, is_success = drone.get_frame()
                    time.sleep(0.2)


                    # Verify that the simulator camera returned a valid frame
                    if is_success and frame is not None:
                        print("SUCCESS: Simulator camera frame received!")
                        if frame_number == 0:
                            cv2.imwrite("mission4_simulator_frame.jpg", frame)
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
                        # Detect human body landmarks in the simulator camera frame
                        simulator_results = detector.detect_for_video(mp_frame, frame_timestamp_ms)
                        # Check whether the simulator frame contains a detected human
                        if simulator_results.pose_landmarks:
                            print("SUCCESS: Human detected in simulator camera frame!")
                            # Display the number of detected body landmarks
                            print("Simulator body landmarks:", len(simulator_results.pose_landmarks[0]))
                            # Store the detected body landmarks for tracking calculations
                            simulator_body = simulator_results.pose_landmarks[0]
                            # Identify the left and right shoulder landmarks
                            simulator_left_shoulder = simulator_body[11]
                            simulator_right_shoulder = simulator_body[12]
                            # Calculate the horizontal center between both shoulders
                            simulator_shoulder_center_x = (
                                simulator_left_shoulder.x + simulator_right_shoulder.x
                            ) / 2
                            # Calculate the apparent width between both shoulders
                            simulator_shoulder_width = abs(
                                simulator_left_shoulder.x - simulator_right_shoulder.x
                            )
                            # Display simulator tracking measurements
                            print("Simulator shoulder center X:", round(simulator_shoulder_center_x, 3))
                            print("Simulator shoulder width:", round(simulator_shoulder_width, 3))
                            # Define the horizontal tracking boundaries
                            SIMULATOR_CENTER_LEFT = 0.40
                            SIMULATOR_CENTER_RIGHT = 0.60
                            # Determine the person's horizontal position
                            if simulator_shoulder_center_x < SIMULATOR_CENTER_LEFT:
                                simulator_horizontal_position = "LEFT"
                            elif simulator_shoulder_center_x > SIMULATOR_CENTER_RIGHT:
                                simulator_horizontal_position = "RIGHT"
                            else:
                                simulator_horizontal_position = "CENTERED"
                            # Display the detected horizontal position
                            print("Simulator horizontal position:", simulator_horizontal_position)
                            # Define shoulder-width boundaries for distance estimation
                            SIMULATOR_MIN_SHOULDER_WIDTH = 0.15
                            SIMULATOR_MAX_SHOULDER_WIDTH = 0.30
                            # Determine the person's apparent distance
                            if simulator_shoulder_width < SIMULATOR_MIN_SHOULDER_WIDTH:
                                simulator_distance_status = "TOO FAR"
                            elif simulator_shoulder_width > SIMULATOR_MAX_SHOULDER_WIDTH:
                                simulator_distance_status = "TOO CLOSE"
                            else:
                                simulator_distance_status = "GOOD DISTANCE"
                            # Display the simulator distance classification
                            print("Simulator distance status:", simulator_distance_status)
                            # Select the simulated horizontal follower action
                            if simulator_horizontal_position == "LEFT":
                                simulator_horizontal_action = "MOVE LEFT"
                            elif simulator_horizontal_position == "RIGHT":
                                simulator_horizontal_action = "MOVE RIGHT"
                            else:
                                simulator_horizontal_action = "HOLD POSITION"

                            # Display the simulated horizontal action
                            print("Simulator horizontal action:", simulator_horizontal_action)
                            # Select the simulated distance follower action
                            if simulator_distance_status == "TOO FAR":
                                simulator_distance_action = "MOVE FORWARD"
                            elif simulator_distance_status == "TOO CLOSE":
                                simulator_distance_action = "MOVE BACKWARD"
                            else:
                                simulator_distance_action = "HOLD DISTANCE"

                            # Display the simulated distance action
                            print("Simulator distance action:", simulator_distance_action)
                        else:
                            print("WARNING: No human detected in simulator camera frame.")
                            # Select safe simulated actions when the target is lost
                            simulator_horizontal_action = "STOP/HOVER"
                            simulator_distance_action = "STOP/HOVER"

                            # Display the target-loss safety decision
                            print("SAFETY: Simulator target lost. STOP/HOVER selected.")
                    else:
                        print("WARNING: Simulator camera frame unavailable.")
                        # Select safe simulated actions when the camera frame is unavailable
                        simulator_horizontal_action = "STOP/HOVER"
                        simulator_distance_action = "STOP/HOVER"

                        # Display the camera-loss safety decision
                        print("SAFETY: Camera frame unavailable. STOP/HOVER selected.")
                    # Confirm completion of the current simulator frame
                    print("Simulator frame processing complete:", frame_number + 1)

            finally:
                # Release simulator resources even if an error occurs
                drone.shutdown()
                print("Simulator shutdown completed.")
            print("Simulator camera access enabled.")
        else:
            print("Simulator camera access disabled.")
    print("VIDEO mode detector closed safely.")