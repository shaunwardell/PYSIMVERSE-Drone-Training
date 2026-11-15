import time
from pysimverse import Drone

drone = Drone()
connected = False
airborne = False

successful_frames = 0
failed_frames = 0

try:
    print("MISSION 5: CAMERA RELIABILITY TEST")

    drone.connect()
    connected = True
    drone.streamon()

    print("Taking off...")
    drone.take_off(takeoff_height=30)
    airborne = True

    print("Hovering and checking camera for 10 seconds...")

    start_time = time.monotonic()

    while time.monotonic() - start_time < 10:
        frame, is_success = drone.get_frame()

        if is_success and frame is not None:
            successful_frames += 1
        else:
            failed_frames += 1

        time.sleep(0.05)

    total_frames = successful_frames + failed_frames

    print("\nCAMERA TEST RESULTS")
    print(f"Successful frames: {successful_frames}")
    print(f"Failed frames: {failed_frames}")

    if total_frames > 0:
        success_rate = successful_frames / total_frames * 100
        print(f"Success rate: {success_rate:.1f}%")

except Exception as error:
    print("Camera test error:", error)

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

    print("Camera reliability test complete.")