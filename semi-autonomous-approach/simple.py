import time
import logging
from pymavlink import mavutil
from gpiar_db.database import db
from gpiar_db.models import Mission, Image
from typing import NoReturn
from live_feed import PicameraStreamingServer
from image_processor import ImageProcessor
from auto_capture import AutoCapture


def init_db() -> None:
    db.connect()
    db.create_tables([Mission, Image], safe=True)


def create_mission() -> Mission:
    mission =  Mission.create(
        name="Fenswood Mission",
        altitude=50,
        is_rhino_detected=True,
        takeoff_location_lat=34.0000,
        takeoff_location_lon=-118.0000,
    )
    return mission


def connect_vehicle() -> mavutil.mavtcp:
    # TODO: Change to serial port
    master: mavutil.mavtcp = mavutil.mavlink_connection("tcp:127.0.0.1:14550")
    logging.info("Waiting for heartbeat...")
    master.wait_heartbeat()
    logging.info(f"Heartbeat received from system {master.target_system}, component {master.target_component}")

    return master


def live_feed():
    streamer = PicameraStreamingServer()
    streamer.start()


def process_batch():
    pass


def listen_to_cmds(master) -> NoReturn:
    while True:
        msg = master.recv_match(type='STATUSTEXT', blocking=True)
        if msg:
            text = msg.text.lower()
            if 'imagestartcapture' in text:

                # TODO: Add start image capture logic
                logging.info("Received ImageStartCapture command")

                auto_capture = AutoCapture(interval=1, save_dir="capture-images")
                auto_capture.capture_loop(master)

            elif 'imagestopcapture' in text:
                # TODO: Add stop image capture logic
                logging.info("Received ImageStopCapture command")
            elif 'scripting' in text:
                # TODO: Add proccessing spot logic
                logging.info("Received DO_SEND_SCRIPT_MESSAGE command")



def main() -> NoReturn:
    logging.basicConfig(
        # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    )
    init_db()
    master = connect_vehicle()
    live_feed()
    listen_to_cmds(master)



if __name__ == '__main__':
    main()

