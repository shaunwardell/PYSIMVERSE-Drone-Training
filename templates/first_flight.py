
from pysimverse import Drone

# Create a drone controller
drone = Drone()

# Connect to the PYSIMVERSE simulator
drone.connect()

# Take off to a height of 100
drone.take_off(takeoff_height=100)

# Land the drone
drone.land()
