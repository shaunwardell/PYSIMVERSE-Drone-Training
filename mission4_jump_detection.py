
import cv2
import time
import mediapipe as mp

from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ==========================================
# MISSION 4: JUMP DETECTION
# ==========================================

MODEL_PATH = "models/pose_landmarker_lite.task"

SMOOTHING_FRAMES = 7
TAKEOFF_VELOCITY = -0.22
LANDING_VELOCITY = 0.08
MIN_JUMP_RISE = 0.035
DEBOUNCE_SECONDS = 0.6

DRONE_CONTROL_ENABLED = False

jump_count = 0
jump_state = "READY"
last_jump_time = 0.0

hip_history = deque(maxlen=SMOOTHING_FRAMES)
previous_smoothed_hip = None
previous_frame_time = None
takeoff_hip_y = None
last_timestamp_ms = -1


# ==========================================
# MEDIAPIPE SETUP
# ==========================================

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1
)

detector = vision.PoseLandmarker.create_from_options(options)

camera = cv2.VideoCapture(0)

print("Mission 4: Jump Detection")
print("Press Q to quit.")


# ==========================================
# WEBCAM LOOP
# ==========================================

try:
    if not camera.isOpened():
        print("ERROR: Webcam could not be opened.")

    else:
        while True:
            success, frame = camera.read()

            if not success or frame is None:
                print("WARNING: Webcam frame unavailable.")
                break

            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_frame = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            current_time = time.monotonic()

            timestamp_ms = max(
                time.monotonic_ns() // 1_000_000,
                last_timestamp_ms + 1
            )

            last_timestamp_ms = timestamp_ms

            results = detector.detect_for_video(
                mp_frame,
                timestamp_ms
            )

            if results.pose_landmarks:
                body = results.pose_landmarks[0]

                left_hip = body[23]
                right_hip = body[24]

                hip_y = (
                    left_hip.y + right_hip.y
                ) / 2

                hip_history.append(hip_y)

                smoothed_hip_y = (
                    sum(hip_history) / len(hip_history)
                )

                # Calculate vertical hip velocity
                if (
                    previous_smoothed_hip is not None
                    and previous_frame_time is not None
                ):
                    delta_time = (
                        current_time - previous_frame_time
                    )

                    if delta_time > 0:
                        vertical_velocity = (
                            smoothed_hip_y
                            - previous_smoothed_hip
                        ) / delta_time
                    else:
                        vertical_velocity = 0.0

                else:
                    vertical_velocity = 0.0

                # Negative velocity means moving upward.
                # Positive velocity means moving downward.

                if jump_state == "READY":

                    if (
                        vertical_velocity < TAKEOFF_VELOCITY
                        and current_time - last_jump_time
                        >= DEBOUNCE_SECONDS
                        and len(hip_history)
                        == SMOOTHING_FRAMES
                    ):
                        jump_state = "RISING"
                        takeoff_hip_y = smoothed_hip_y

                elif jump_state == "RISING":

                    if (
                        takeoff_hip_y is not None
                        and takeoff_hip_y - smoothed_hip_y
                        >= MIN_JUMP_RISE
                    ):
                        jump_count += 1
                        last_jump_time = current_time
                        jump_state = "AIRBORNE"

                        print(
                            "JUMP DETECTED! Total:",
                            jump_count
                        )

                    elif vertical_velocity >= LANDING_VELOCITY:
                        # Reject a small upward movement.
                        jump_state = "READY"
                        takeoff_hip_y = None

                elif jump_state == "AIRBORNE":

                    if vertical_velocity >= LANDING_VELOCITY:
                        jump_state = "LANDING"

                elif jump_state == "LANDING":

                    if (
                        abs(vertical_velocity) < 0.08
                        and current_time - last_jump_time
                        >= DEBOUNCE_SECONDS
                    ):
                        jump_state = "READY"
                        takeoff_hip_y = None

                previous_smoothed_hip = smoothed_hip_y
                previous_frame_time = current_time

                # Display hip position
                frame_height, frame_width = frame.shape[:2]

                hip_x = (
                    left_hip.x + right_hip.x
                ) / 2

                center_x = int(hip_x * frame_width)
                center_y = int(hip_y * frame_height)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    10,
                    (0, 255, 0),
                    -1
                )

                cv2.putText(
                    frame,
                    f"Velocity: {vertical_velocity:.3f}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

            else:
                # Reset tracking when the person disappears.
                hip_history.clear()

                previous_smoothed_hip = None
                previous_frame_time = None
                takeoff_hip_y = None

                jump_state = "READY"

                cv2.putText(
                    frame,
                    "NO BODY DETECTED",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            # Display jump counter
            cv2.putText(
                frame,
                f"Jumps: {jump_count}",
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 255),
                3
            )

            cv2.putText(
                frame,
                f"State: {jump_state}",
                (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Mission 4 - Jump Detection",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.release()
    detector.close()
    cv2.destroyAllWindows()

    print()
    print("Mission 4 webcam test completed.")
    print("Total jumps detected:", jump_count)
