
# Safety lock: Keep actual drone commands disabled
DRONE_CONTROL_ENABLED = False


def decide_direction(x_position):
    if x_position < 0.40:
        return "TURN LEFT"
    elif x_position > 0.60:
        return "TURN RIGHT"
    else:
        return "STAY CENTERED"

def decide_distance(shoulder_width):
    if shoulder_width < 0.15:
        return "MOVE FORWARD"
    elif shoulder_width > 0.30:
        return "MOVE BACKWARD"
    else:
        return "HOLD DISTANCE"






# Test all three simulated body positions
test_positions = [0.20, 0.39, 0.40, 0.50, 0.60, 0.61, 0.80]

# Test simulated shoulder widths
test_widths = [0.10, 0.14, 0.15, 0.20, 0.30, 0.31, 0.40]

for width in test_widths:
    result = decide_distance(width)
    print("TEST SHOULDER WIDTH:", width, "->", result)

print()


for position in test_positions:
    result = decide_direction(position)
    print("TEST POSITION:", position, "->", result)

print()

import mediapipe as mp

# Access MediaPipe's computer vision tools
vision = mp.tasks.vision

# Select the body pose detection class
PoseLandmarker = vision.PoseLandmarker

print("Mission 4: Body Follower")
print("MediaPipe version:", mp.__version__)
print("Body pose detection tools are available!")

# Load the trained body detection model
model_path = "models/pose_landmarker_lite.task"

with PoseLandmarker.create_from_model_path(model_path) as detector:
    print("SUCCESS: Body detection model loaded!")

    # Load our body test photograph
    # Prepare a list of images for future multi-frame testing

    image_paths = [
        "test_images/body_test.jpg",
        "test_images/no_human_test.jpg"
    ]
    # Process each photograph in our image list
    for image_path in image_paths:
        print("PROCESSING IMAGE:", image_path)
        image = mp.Image.create_from_file(image_path)
        results = detector.detect(image)


        # Display detection results
        if results.pose_landmarks:
            print("SUCCESS: Human body detected!")

            for body in results.pose_landmarks:
                print("Body landmarks detected:", len(body))

                # Landmark 0 represents the nose
                nose = body[0]

                print("Nose X position:", round(nose.x, 3))
                print("Nose Y position:", round(nose.y, 3))

                # Identify both shoulders
                left_shoulder = body[11]
                right_shoulder = body[12]

                # Calculate the horizontal center of the shoulders
                shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2

                print("Shoulder center X:", round(shoulder_center_x, 3))

                # Measure the apparent width between both shoulders
                shoulder_width = abs(right_shoulder.x - left_shoulder.x)

                print("Shoulder width:", round(shoulder_width, 3))
                # Calculate simulated distance decision
                distance_decision = decide_distance(shoulder_width)

                print("SIMULATED DISTANCE DECISION:", distance_decision)



                # Decide which direction the drone should face
                direction = decide_direction(shoulder_center_x)

                print("SIMULATED DRONE DECISION:", direction)
                # Check safety lock before any future drone control
                if not DRONE_CONTROL_ENABLED:
                    print("SAFETY LOCK ACTIVE: Drone commands disabled.")
                else:
                    print("DRONE CONTROL ENABLED: No commands implemented.")


        else:
            print("No human body detected in the photograph.")
            print("SIMULATED SAFETY DECISION: STOP/HOVER - TARGET LOST")


print("Body detection model closed safely.")
