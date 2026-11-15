"""Mission 5: red-line follower for the PYSIMVERSE simulator."""
import math
import time
import cv2
import numpy as np
from cvzone.ColorModule import ColorFinder
from pysimverse import Drone

RED_HSV = {"hmin": 0, "smin": 120, "vmin": 100, "hmax": 10, "smax": 255, "vmax": 255}
TAKEOFF_HEIGHT = 30
WINDOW_NAME = "Mission 5 - Path Direction Tracker"

# Conservative initial values. Adjust only after observing a complete test.
FORWARD_STRAIGHT = 28
FORWARD_CURVE = 6
MAX_YAW = 12
MAX_MISSING_SECONDS = 0.4

finder = ColorFinder(False)
drone = Drone()
connected = False
airborne = False
last_good_frame = time.monotonic()
previous_near_x = None


def command(forward=0, yaw=0):
    drone.send_rc_control(left_right=0, forward_backward=int(forward), up_down=0, yaw=int(yaw))


def line_at_row(mask, row_fraction, expected_x=None):
    """Return center of the most plausible red segment in a narrow horizontal strip."""
    h, w = mask.shape
    y = int(h * row_fraction)
    strip = mask[max(0, y - 8):min(h, y + 9)]
    column_counts = np.count_nonzero(strip, axis=0)
    active = column_counts >= 4
    # Segment the line by contiguous columns, rejecting tiny specks.
    padded = np.r_[False, active, False]
    edges = np.diff(padded.astype(np.int8))
    starts = np.flatnonzero(edges == 1)
    ends = np.flatnonzero(edges == -1)
    segments = [(int(a), int(b)) for a, b in zip(starts, ends) if b - a >= 5]
    if not segments:
        return None, y
    if expected_x is None:
        segment = max(segments, key=lambda ab: ab[1] - ab[0])
    else:
        segment = min(segments, key=lambda ab: abs((ab[0] + ab[1]) / 2 - expected_x))
    return (segment[0] + segment[1]) // 2, y


try:
    print("Mission 5: Path Direction Tracker")
    drone.connect()
    connected = True
    drone.streamon()
    drone.take_off(takeoff_height=TAKEOFF_HEIGHT)
    airborne = True
    cv2.namedWindow(WINDOW_NAME)
    print("Press Q in the camera window to land.")

    while True:
        frame, ok = drone.get_frame()
        now = time.monotonic()
        if not ok or frame is None:
            if now - last_good_frame >= MAX_MISSING_SECONDS:
                command(0, 0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue
        last_good_frame = now
        frame = cv2.resize(frame, (640, 480))
        _, mask = finder.update(frame, RED_HSV)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        h, w = mask.shape
        mid = w // 2

        # Track a connected-looking sequence from near to far.
        near, near_y = line_at_row(mask, 0.82, previous_near_x)
        middle, middle_y = line_at_row(mask, 0.58, near)
        far, far_y = line_at_row(mask, 0.34, middle)
        previous_near_x = near

        forward = 0
        yaw = 0
        status = "LINE LOST: HOVER"
        if near is not None and middle is not None:
            # Heading is based on how the line moves from near to middle.
            # This avoids averaging an entire S-shaped path into one point.
            heading = math.degrees(math.atan2(middle - near, near_y - middle_y))
            lateral = (near - mid) / (w / 2)
            steering = 0.17 * heading + 5.0 * lateral
            if far is not None:
                far_heading = math.degrees(math.atan2(far - middle, middle_y - far_y))
                steering += 0.035 * far_heading
            yaw = int(np.clip(round(steering), -MAX_YAW, MAX_YAW))
            forward = FORWARD_CURVE if abs(heading) > 18 else FORWARD_STRAIGHT
            status = "FOLLOWING"
        elif near is not None:
            # Without heading information, don't spin or charge ahead.
            status = "NEAR ONLY: HOVER"
        elif middle is not None or far is not None:
            status = "FAR ONLY: HOVER"
        command(forward, yaw)

        display = frame.copy()
        cv2.line(display, (mid, 0), (mid, h), (255, 0, 0), 2)
        for x, y, color in [(near, near_y, (0, 255, 0)),
                            (middle, middle_y, (0, 255, 255)),
                            (far, far_y, (255, 0, 255))]:
            cv2.line(display, (0, y), (w, y), color, 1)
            if x is not None:
                cv2.circle(display, (x, y), 8, color, -1)
        if near is not None and middle is not None:
            cv2.line(display, (near, near_y), (middle, middle_y), (255, 255, 255), 2)
        cv2.putText(display, f"{status}  Forward:{forward}  Yaw:{yaw}",
                    (8, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.53, (255, 255, 255), 2)
        side_by_side = np.hstack((display, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)))
        cv2.imshow(WINDOW_NAME, cv2.resize(side_by_side, None, fx=0.4, fy=0.4))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
except Exception as exc:
    print("Mission 5 error:", repr(exc))
finally:
    if connected:
        try:
            command(0, 0)
            if airborne:
                drone.land()
        finally:
            drone.shutdown()
    cv2.destroyAllWindows()
    print("Mission 5 stopped.")
