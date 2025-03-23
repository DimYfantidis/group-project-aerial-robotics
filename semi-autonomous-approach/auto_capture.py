import cv2
import time
import os
import uuid
import logging
from image import Image
from mission import Mission, MissionStatus


class AutoCapture:

    def __init__(self, interval=1, save_dir="capture-images", pi_environ=True):
        """
        Initializes the AutoCapture instance.
        """
        self.interval = interval
        self.save_dir = save_dir
        self.counter = 0
        self.pi_environ = pi_environ

        # Initialize and start the camera if in Raspberry Pi environment
        if self.pi_environ:
            from picamera2 import Picamera2
            self.camera = Picamera2()
            self.camera.start()
        else:
            self.camera = None

        self.is_capture_enabled = False

        # Ensure the save directory exists
        os.makedirs(self.save_dir, exist_ok=True)

        # Retrieve the active mission record from the database
        self.mission = Mission.get(Mission.status == MissionStatus.ACTIVE)
        logging.info("AutoCapture initialized.")

    def stop_capture(self):
        self.is_capture_enabled = False

    def capture_loop(self, lat, lon, yaw):
        """
        Continuously captures images from the camera using the latest telemetry data.
        """
        self.is_capture_enabled = True

        while self.is_capture_enabled:
            # Capture an image from the camera
            if self.pi_environ:
                frame = self.camera.capture_array()
            else:
                import numpy as np
                # Generate a dummy image (480x640 with 3 channels)
                frame = (255 * np.random.random((480, 640, 3))
                         ).astype(np.uint8)

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
                yaw=yaw[0],
                lat=lat[0],
                lon=lon[0]
            )

            self.counter += 1
            time.sleep(self.interval)
