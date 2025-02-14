import cv2
import time
import os
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()

interval = 1  # In seconds
counter = 0
SAVE_DIR = "capture-images"
# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

while True:
    timestamp = time.strftime("%Y%m%d-%H%M%S")  # Use timestamp as a part of filename to avoid overwriting
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    filename = f"{SAVE_DIR}/image_{timestamp}.png"
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    
    counter += 1
    time.sleep(interval)