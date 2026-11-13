
import time
import cv2
from pysimverse import Drone

# Create and connect to the drone
drone = Drone()
drone.connect()
# Take off before capturing the image
drone.take_off(takeoff_height=130)
# Move toward the snapshot targetz
drone.move_forward(230)
# Turn right to face the snapshot targetz
drone.rotate(345)

# Start the drone's camera
drone.streamon()

# Allow time for the camera to initialize
time.sleep(2)

# # Capture an image
# frame, is_success = drone.get_frame()
#
# # Save the image if capture was successful
# if is_success and frame is not None:
#
#     photo_saved = cv2.imwrite("mission2_photo.jpg", frame)
#
#     if photo_saved:
#         print("Photo saved successfully!")
#     else:
#         print("ERROR: Photo could not be saved.")
#
# else:
#     print("Failed to capture an image.")

# Turn off the camera
drone.streamoff()
