
import cv2
import time
import mediapipe as mp

from collections import deque
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pysimverse import Drone


# ==========================================
# MISSION 4: JUMP-CONTROLLED DRONE
# ==========================================

MODEL_PATH = "models/pose_landmarker_lite.task"

SMOOTHING_FRAMES = 7
TAKEOFF_VELOCITY = -0.28
LANDING_VELOCITY = 0.08
MIN_JUMP_RISE = 0.040
DEBOUNCE_SECONDS = 0.8

# PYSIMVERSE controls
DRONE_CONTROL_ENABLED = False
RC_UP_SPEED = 50
JUMP_PULSE_SECONDS = 0.40

jump_count = 0
peak_upward_velocity = 0.0
jump_state = "READY"
last_jump_time = 0.0

hip_history = deque(maxlen=SMOOTHING_FRAMES)
previous_smoothed_hip = None
previous_frame_time = None
takeoff_hip_y = None
last_timestamp_ms = -1

# Controls how long the drone rises after a jump.
rise_until = 0.0

drone = None
camera = None
detector = None

print("Mission 4: Jump-Controlled Drone")
print("Drone control enabled:", DRONE_CONTROL_ENABLED)
print("Press Q to quit.")


# ==========================================
# INITIALIZE MEDIAPIPE AND PYSIMVERSE
# ==========================================

try:
    base_options = python.BaseOptions(
        model_asset_path=MODEL_PATH
    )

    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1
    )

    detector = vision.PoseLandmarker.create_from_options(
        options
    )

    if DRONE_CONTROL_ENABLED:
        drone = Drone()
        drone.connect()
        print("SUCCESS: Connected to PYSIMVERSE!")
    else:
        print("SAFETY MODE: Drone commands disabled.")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Webcam could not be opened.")

    else:
        print("SUCCESS: Webcam connected!")

        # ==========================================
        # LIVE WEBCAM LOOP
        # ==========================================

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

            vertical_velocity = 0.0
            jump_detected = False
            body_detected = bool(results.pose_landmarks)

            if body_detected:
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

                # Record the strongest upward movement.
                if vertical_velocity < peak_upward_velocity:
                    peak_upward_velocity = vertical_velocity

                # Detect upward movement.
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
                        jump_detected = True

                        # Start a short upward RC pulse.
                        rise_until = (
                            current_time + JUMP_PULSE_SECONDS
                        )

                        print(
                            "JUMP DETECTED! Total:",
                            jump_count
                        )

                    elif vertical_velocity >= LANDING_VELOCITY:
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


                # ==========================================
                # DRAW FULL-BODY POSE SKELETON
                # ==========================================

                frame_height, frame_width = frame.shape[:2]

                # Connections between MediaPipe body landmarks
                pose_connections = [
                    (11, 12),  # Shoulders
                    (11, 13), (13, 15),  # Left arm
                    (12, 14), (14, 16),  # Right arm
                    (11, 23), (12, 24),  # Torso
                    (23, 24),  # Hips
                    (23, 25), (25, 27),  # Left leg
                    (24, 26), (26, 28),  # Right leg
                    (27, 29), (29, 31),  # Left foot
                    (28, 30), (30, 32)   # Right foot
                ]

                # Draw lines connecting body joints
                for start_index, end_index in pose_connections:
                    start = body[start_index]
                    end = body[end_index]

                    start_point = (
                        int(start.x * frame_width),
                        int(start.y * frame_height)
                    )

                    end_point = (
                        int(end.x * frame_width),
                        int(end.y * frame_height)
                    )

                    cv2.line(
                        frame,
                        start_point,
                        end_point,
                        (0, 255, 255),
                        2
                    )

                # Draw individual body landmarks
                for landmark in body:
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (0, 255, 0),
                        -1
                    )

                # Highlight the hip center used for jump detection
                hip_x = (
                    left_hip.x + right_hip.x
                ) / 2

                center_x = int(hip_x * frame_width)
                center_y = int(hip_y * frame_height)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    10,
                    (0, 0, 255),
                    -1
                )


            else:
                # Stop upward movement if tracking is lost.
                hip_history.clear()

                previous_smoothed_hip = None
                previous_frame_time = None
                takeoff_hip_y = None

                jump_state = "READY"
                rise_until = 0.0

                cv2.putText(
                    frame,
                    "NO BODY DETECTED",
                    (20, 165),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            # ==========================================
            # DRONE ALTITUDE CONTROL
            # ==========================================

            if body_detected and current_time < rise_until:
                rc_up = RC_UP_SPEED
            else:
                rc_up = 0

            if DRONE_CONTROL_ENABLED and drone is not None:
                drone.send_rc_control(
                    left_right=0,
                    forward_backward=0,
                    up_down=rc_up,
                    yaw=0
                )

            # ==========================================
            # ON-SCREEN INFORMATION
            # ==========================================

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

            cv2.putText(
                frame,
                f"Velocity: {vertical_velocity:.3f}",
                (20, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"RC UP: {rc_up}",
                (20, 205),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Mission 4: Jump-Controlled Drone",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    # ==========================================
    # SAFE SHUTDOWN
    # ==========================================

    if drone is not None:
        try:
            drone.send_rc_control(
                left_right=0,
                forward_backward=0,
                up_down=0,
                yaw=0
            )

            drone.land()
            print("SUCCESS: Drone landed safely.")

        except Exception as error:
            print("Drone shutdown warning:", error)

    if camera is not None:
        camera.release()

    if detector is not None:
        detector.close()

    cv2.destroyAllWindows()

    print()
    print("Mission 4 completed.")
    print("Total jumps detected:", jump_count)
    print(
        "Peak upward velocity:",
        round(peak_upward_velocity, 3)
    )
    print("Drone resources released.")
