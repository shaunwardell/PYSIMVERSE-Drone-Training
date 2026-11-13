
import time
from pysimverse import Drone

# Create our drone and connect to the simulator
drone = Drone()
drone.connect()

# Take off to a height of 100
drone.take_off(takeoff_height=100)

# Navigate toward the landing target
drone.move_forward(270)
drone.move_right(273)

# Land on the target
drone.land()

# Allow time for the mission to finish
time.sleep(5)
