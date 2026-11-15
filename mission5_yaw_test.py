import time
from pysimverse import Drone

drone = Drone()
connected = False
airborne = False

try:
    print("MISSION 5: YAW DIRECTION TEST")

    drone.connect()
    connected = True
    drone.streamon()

    print("Taking off...")
    drone.take_off(takeoff_height=30)
    airborne = True

    print("Hovering for 2 seconds...")
    time.sleep(2)

    print("Testing POSITIVE yaw (+5) for 1 second...")

    drone.send_rc_control(
        left_right=0,
        forward_backward=0,
        up_down=0,
        yaw=5
    )

    time.sleep(1)

    print("Stopping rotation...")

    drone.send_rc_control(
        left_right=0,
        forward_backward=0,
        up_down=0,
        yaw=0
    )

    time.sleep(2)

except Exception as error:
    print("Test error:", error)

finally:
    if connected:
        drone.send_rc_control(
            left_right=0,
            forward_backward=0,
            up_down=0,
            yaw=0
        )

        if airborne:
            print("Landing...")
            drone.land()

        drone.shutdown()

    print("Yaw direction test complete.")