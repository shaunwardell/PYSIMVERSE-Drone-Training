import cv2
import cvzone
from cvzone.ColorModule import ColorFinder

# Initialize CVZone ColorFinder with HSV sliders enabled
my_color_finder = ColorFinder(True)

# Open the computer's webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    raise SystemExit

print("MISSION 5: HSV Color Tuner")
print("Use the HSV sliders to isolate your target color.")
print("Press Q to quit.")

try:
    while True:
        success, frame = cap.read()

        if not success:
            print("ERROR: Could not read webcam frame.")
            break

        # Resize the image to fit comfortably on screen
        frame = cv2.resize(frame, (640, 480))

        # Detect color using the interactive HSV sliders
        img_color, mask = my_color_finder.update(frame)

        # Display original image, detected color, and mask
        img_stack = cvzone.stackImages(
            [frame, img_color, mask],
            2,
            0.5
        )

        cv2.imshow("Mission 5 - HSV Color Tuner", img_stack)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("HSV tuner closed.")