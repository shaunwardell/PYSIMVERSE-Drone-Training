
from pysimverse import Drone

# Create our drone controller
drone = Drone()

# Connect to the simulator
drone.connect()

# Take off
drone.take_off(takeoff_height=100)

# Send neutral RC controls
# All four movement values are zero
drone.send_rc_control(
    left_right=0,
    forward_backward=0,
    up_down=0,
    yaw=0
)

# Land the drone
drone.land()
