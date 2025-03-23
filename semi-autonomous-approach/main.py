import time
import os
import logging
from pymavlink import mavutil
from database import db
from mission import Mission
from image import Image
from typing import NoReturn
from image_processor import ImageProcessor
from auto_capture import AutoCapture
from threading import Thread

PI_ENVIRON = False


def init_db() -> None:
    db.connect()
    db.create_tables([Mission, Image], safe=True)


def create_mission() -> Mission:
    mission = Mission.create(
        name="Fenswood Mission",
        altitude=50,
        takeoff_location_lat=51.42341782233007,
        takeoff_location_lon=-2.671550567532177
    )
    return mission


def connect_vehicle() -> mavutil.mavtcp:
    master = mavutil.mavlink_connection("tcp:127.0.0.1:14550")
    logging.info("Waiting for heartbeat...")
    master.wait_heartbeat()
    logging.info(
        f"Heartbeat received from system {master.target_system}, component {master.target_component}")
    return master


def live_feed():
    if PI_ENVIRON:
        from live_feed import PicameraStreamingServer
        streamer = PicameraStreamingServer()
        streamer.start()


def update_position(master, lat, lon, yaw):
    """
    Continuously listen for GLOBAL_POSITION_INT messages and update the position.
    """
    while True:
        msg = master.recv_match(blocking=True)
        if msg is None:
            continue
        if msg.get_type() == 'GLOBAL_POSITION_INT':
            lat[0] = msg.lat / 1e7
            lon[0] = msg.lon / 1e7
            yaw_val = msg.hdg / 100.0 if msg.hdg != 65535 else 0.0
            yaw[0] = yaw_val
            logging.info(
                f"Current position: ({lat[0]}, {lon[0]}), Yaw: {yaw[0]}")


def process_images_loop(processor: ImageProcessor):
    """
    Continuously process unprocessed images in the background.
    """
    while True:
        processor.process_and_save_images(os.path.abspath("./capture-images"))
        time.sleep(5)  # Adjust processing interval as needed


def main() -> NoReturn:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )
    init_db()
    create_mission()
    master = connect_vehicle()
    live_feed()

    # Shared mutable variables for telemetry data (lat, lon, yaw)
    lat = [0.0]
    lon = [0.0]
    yaw = [0.0]

    # Instantiate auto capture and image processor
    auto_capture = AutoCapture(
        interval=1, save_dir="capture-images", pi_environ=PI_ENVIRON)
    # Other heights:
    # > 25 meters: (21.832760, 16.680318)
    # > 30 meters: (26.199312, 20.016382)
    # > 35 meters: (30.565865, 23.352445)
    # > 50 meters: (43.665521, 33.360636)
    image_processor = ImageProcessor(
        './yolo_model/best.pt', visible_ground_dims=(21.832760, 16.680318))

    # Start telemetry thread to update position data
    telemetry_thread = Thread(target=update_position, args=(
        master, lat, lon, yaw), daemon=True)
    telemetry_thread.start()

    # Start auto capture thread to capture images using the latest telemetry data
    capture_thread = Thread(target=auto_capture.capture_loop,
                            args=(lat, lon, yaw), daemon=True)
    capture_thread.start()

    # Start image processing thread to process captured images in the background
    processing_thread = Thread(
        target=process_images_loop, args=(image_processor,), daemon=True)
    processing_thread.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
