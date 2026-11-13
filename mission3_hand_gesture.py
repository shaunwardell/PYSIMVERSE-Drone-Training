
import mediapipe as mp
# Safety lock: Keep actual drone commands disabled
DRONE_CONTROL_ENABLED = False

print("Drone control enabled:", DRONE_CONTROL_ENABLED)

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
