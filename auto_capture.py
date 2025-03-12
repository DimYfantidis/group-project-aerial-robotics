import cv2
import time
import os
import uuid
import logging
from picamera2 import Picamera2
from gpiar_db.models import Image, Mission, MissionStatus
from pymavlink import mavutil


class AutoCapture:

    def __init__(self, interval=1, save_dir="capture-images"):
        """
        Initializes the AutoCapture instance.

        Args:
            interval (int, optional): Time interval (in seconds) between captures. Defaults to 1.
            save_dir (str, optional): Directory to save captured images. Defaults to "capture-images".
        """
        self.interval = interval
        self.save_dir = save_dir
        self.counter = 0
        
        # Initialize and start the camera
        self.camera = Picamera2()
        self.camera.start()

        self.is_capture_enabled = False

        # Ensure the save directory exists
        os.makedirs(self.save_dir, exist_ok=True)

        # Retrieve the active mission record from the database
        self.mission = Mission.get(Mission.status == MissionStatus.ACTIVE)
        logging.info("AutoCapture initialized.")


    def stop_capture(self):
        self.is_capture_enabled = False


    def capture_loop(self, master: mavutil.mavtcp):
        """
        Continuously captures images from the camera while listening for MAVLink messages.

        Args:
            master (mavutil.mavtcp): The MAVLink master connection used to receive messages.
        """
        self.is_capture_enabled = True

        while self.is_capture_enabled:
            # Receive a MAVLink message of type 'GLOBAL_POSITION_INT'
            msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if msg:
                # Convert latitude and longitude from 1e7 degrees to standard degrees
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7

                # Convert heading from centidegrees to degrees
                yaw = msg.hdg / 100.0 if msg.hdg != 65535 else None  # 65535 means undefined
            
            # Capture an image array from the camera
            frame = self.camera.capture_array()
            # Convert the image from RGB to BGR format for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Generate a unique image ID and construct the filename
            current_image_id = uuid.uuid4()
            filename = os.path.join(self.save_dir, f"{current_image_id}.png")
            
            # Save the captured frame as an image file
            cv2.imwrite(filename, frame)
            logging.info(f"Image saved as {filename}")
            
            # Create a record of the image capture in the database
            Image.create(
                path=filename,
                id=current_image_id,
                mission=self.mission,
                yaw=yaw,
                lat=lat,
                lon=lon
            )
            
            # Increment the counter for the number of images captured
            self.counter += 1
            
            # Wait for the defined interval before capturing the next image
            time.sleep(self.interval)

# Example usage:
# Assuming 'master' is your mavutil.mavtcp connection
# auto_capture = AutoCapture(interval=1, save_dir="capture-images")
# auto_capture.capture_loop(master)
