
import mediapipe as mp
import cv2
import time
from pysimverse import Drone

# Safety lock: Keep actual drone commands disabled
DRONE_CONTROL_ENABLED = True
RC_SIDEWAYS_SPEED = 20

print("Drone control enabled:", DRONE_CONTROL_ENABLED)
# Create the PYSIMVERSE drone controller
drone = None
# Connect to PYSIMVERSE only when drone control is enabled
if DRONE_CONTROL_ENABLED:
    drone = Drone()
    drone.connect()
    print("SUCCESS: Connected to PYSIMVERSE!")
else:
    print("SAFETY MODE: Drone connection disabled.")

# Access MediaPipe's computer vision tools
vision = mp.tasks.vision

# Select the hand landmark detection class
HandLandmarker = vision.HandLandmarker

print("Mission 3: Hand Gesture Control")
print("MediaPipe version:", mp.__version__)
print("Hand tracking tools are available!")


# Load the trained hand-tracking model
model_path = "models/hand_landmarker.task"

# Photographs to test automatically
test_images = [
    "test_images/hand_test2.jpg",
    "test_images/fist_test.jpg"
]

# Process each test photograph automatically
with HandLandmarker.create_from_model_path(model_path) as detector:
    for image_path in test_images:
        print("\nTesting image:", image_path)

        image = mp.Image.create_from_file(image_path)

        results = detector.detect(image)

        # Display MediaPipe's handedness classification and confidence
        if results.handedness:
           for detected_hand in results.handedness:
               for category in detected_hand:
                   print("Detected hand:", category.category_name)
                   print("Classification confidence:", round(category.score, 3))

        # Check whether hands were detected
        if results.hand_landmarks:
            print("SUCCESS: Hand detected!")

            for hand in results.hand_landmarks:
                print("Landmarks detected:", len(hand))

                # Landmark 8 represents the index fingertip
                index_finger = hand[8]
                index_joint = hand[6]

                # Identify landmarks for the other three fingers
                middle_tip = hand[12]
                middle_joint = hand[10]

                ring_tip = hand[16]
                ring_joint = hand[14]

                pinky_tip = hand[20]
                pinky_joint = hand[18]

                print("Index fingertip X:", round(index_finger.x, 3))
                print("Index fingertip Y:", round(index_finger.y, 3))
                print("Index joint Y:", round(index_joint.y, 3))

                # Check whether the index fingertip is above its middle joint
                if index_finger.y < index_joint.y:
                    print("GESTURE: Index finger appears extended!")
                else:
                    print("GESTURE: Index finger may be folded!")

                # Count how many fingers appear extended
                extended_fingers = 0

                if index_finger.y < index_joint.y:
                    extended_fingers += 1

                if middle_tip.y < middle_joint.y:
                    extended_fingers += 1

                if ring_tip.y < ring_joint.y:
                    extended_fingers += 1

                if pinky_tip.y < pinky_joint.y:
                    extended_fingers += 1

                print("Extended fingers detected:", extended_fingers)

                # Recognize the gesture
                if extended_fingers == 4:
                    gesture = "OPEN HAND"
                    command = "TAKE OFF"

                elif extended_fingers == 0:
                    gesture = "POSSIBLE FIST"
                    command = "LAND"

                else:
                    gesture = "PARTIALLY OPEN HAND"
                    command = "NO ACTION"

                print("GESTURE RECOGNIZED:", gesture)

                # Check the safety lock before permitting commands
                if not DRONE_CONTROL_ENABLED:
                    print("SAFETY LOCK ACTIVE: Drone commands disabled.")
                else:
                    print("SIMULATED DRONE COMMAND:", command)




        else:
            print("No hands detected in the image.")

# Configure MediaPipe for live video tracking
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

live_options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# Open the computer's webcam
camera = cv2.VideoCapture(0)

# Check whether the webcam opened successfully
if camera.isOpened():
    print("SUCCESS: Webcam connected!")
else:
    print("ERROR: Could not open webcam.")


# Display the live webcam feed

# Create the MediaPipe live hand detector
live_detector = HandLandmarker.create_from_options(live_options)

try:
    while True:
        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Flip the webcam image horizontally for mirror-style tracking
        frame = cv2.flip(frame, 1)

        # Convert the webcam frame for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Generate a timestamp for the current video frame
        timestamp_ms = int(time.monotonic() * 1000)

        # Detect hands in the current webcam frame
        results = live_detector.detect_for_video(mp_image, timestamp_ms)

        # Determine hand position using the wrist landmark
        if results.hand_landmarks:
            hand = results.hand_landmarks[0]
            wrist_x = hand[0].x

            if wrist_x < 0.40:
                direction = "LEFT"
                rc_speed = -RC_SIDEWAYS_SPEED

            elif wrist_x > 0.60:
                direction = "RIGHT"
                rc_speed = RC_SIDEWAYS_SPEED

            else:
                direction = "CENTER"
                rc_speed = 0

            # Display the detected direction
            cv2.putText(
                frame,
                direction,
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                3
            )

        else:
            # Stop sideways movement when no hand is detected
            rc_speed = 0

            cv2.putText(
                frame,
                "NO HAND DETECTED",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # Draw detected hand landmarks on the webcam frame
        if results.hand_landmarks:
            for hand in results.hand_landmarks:
                for landmark in hand:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (0, 255, 0),
                        -1
                    )

        # Send movement commands only when drone control is enabled
        if DRONE_CONTROL_ENABLED and drone is not None:
            drone.send_rc_control(
                left_right=rc_speed,
                forward_backward=0,
                up_down=0,
                yaw=0
            )

        # Display the calculated RC speed
        cv2.putText(
            frame,
            f"RC SPEED: {rc_speed}",
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # Display the webcam feed
        cv2.imshow("Mission 3: Live Hand Tracking", frame)

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # Stop and land the drone when exiting
    try:
        if DRONE_CONTROL_ENABLED and drone is not None:
            drone.send_rc_control(
                left_right=0,
                forward_backward=0,
                up_down=0,
                yaw=0
            )

            drone.land()
            print("SUCCESS: Drone landed safely.")

    finally:
        # Release the webcam
        camera.release()

        # Close the MediaPipe hand detector
        live_detector.close()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

        print("Mission 3: Resources released.")
