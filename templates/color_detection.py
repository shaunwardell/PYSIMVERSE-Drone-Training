
import cv2
import numpy as np

# Create a small black image
image = np.zeros((200, 200, 3), dtype=np.uint8)

# Draw a green rectangle in the image
cv2.rectangle(image, (50, 50), (150, 150), (0, 255, 0), -1)

# Convert the image from BGR to HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the HSV range for green
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])

# Create a mask that identifies green pixels
mask = cv2.inRange(hsv_image, lower_green, upper_green)

# Count how many green pixels were detected
green_pixels = cv2.countNonZero(mask)

print("Green pixels detected:", green_pixels)

if green_pixels > 0:
    print("SUCCESS: Green color detected!")
else:
    print("No green color detected.")
