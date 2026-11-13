
# Keyboard control practice
# No drone connection required

print("Drone Keyboard Control Practice")
print("W = Forward")
print("S = Backward")
print("A = Left")
print("D = Right")
print("Q = Quit")

key = input("Enter a direction: ").lower()

if key == "w":
    print("Forward")
elif key == "s":
    print("Backward")
elif key == "a":
    print("Left")
elif key == "d":
    print("Right")
elif key == "q":
    print("Quit")
else:
    print("Invalid key")
