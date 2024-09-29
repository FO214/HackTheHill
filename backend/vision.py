from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Initialize the camera
picam2 = Picamera2()
picam2.start()

last_position = None
last_time = time.time()
frame_counter = 0  # To save frame images


dx = 0
dy = 0
def set_position_change(chx, chy):
    global dx, dy
    dx += chx
    dy += chy
def get_position_change():
    global dx, dy
    ret = [dx, dy]
    dx = dy = 0
    return ret


def start_vision():
    global last_time, last_position, frame_counter
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        print("Attempting to read a frame...", frame is not None)
        if frame is None:
            print("Error: Failed to capture image.")
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Blur the image to reduce noise
        gray_blurred = cv2.medianBlur(gray, 5)

        # Apply Hough Circle Transform to detect circles
        circles = cv2.HoughCircles(gray_blurred, 
                                cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                param1=100, param2=40,  # Adjusted for higher confidence
                                minRadius=10, maxRadius=100)

        # If some circles are detected, draw the most confident circle
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")

            # Find the most confident circle (with the maximum radius)
            most_confident_circle = max(circles, key=lambda c: c[2])  # c[2] is the radius
            x, y, r = most_confident_circle
            
            # Draw the outer circle on the frame
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
            # Draw the center of the circle
            cv2.circle(frame, (x, y), 3, (0, 0, 255), 3)

            # Check if 0.1 seconds have passed
            current_time = time.time()
            if current_time - last_time >= 0.1:  
                if last_position is not None:
                    dx = x - last_position[0]
                    dy = y - last_position[1]
                    set_position_change(dx, dy)
                    print(f"Change in position: (dx={dx}, dy={dy})")

                # Update last position and time
                last_position = (x, y)
                last_time = current_time

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Clean up
    picam2.stop()

if __name__ == "__main__":
    start_vision()