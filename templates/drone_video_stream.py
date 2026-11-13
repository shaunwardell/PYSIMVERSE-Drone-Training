
from pysimverse import Drone

# Create our drone controller
drone = Drone()

# Connect to the simulator
drone.connect()

# Turn on the drone camera
drone.streamon()


# Retrieve one camera frame and its success status
frame, is_success = drone.get_frame()

# Check whether the camera returned an image
if is_success and frame is not None:
    print("Camera frame received successfully!")
else:
    print("No camera frame received.")


# Turn off the camera stream
drone.streamoff()
