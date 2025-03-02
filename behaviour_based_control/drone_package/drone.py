from typing import Any

import os 
import cv2 
import numpy as np


class Drone:
    """
    **Wrapper class** that retrieves information regarding the UAV's state that are 
    broadcasted using the MAVLink protocol.

    For now this API allows the user to perform mutations on its fields using 
    functions such as `Drone.advance_waypoint`, or `Drone.advance_significant`.

    In reality this should be a read-only API that returns information regarding the UAV's
    current state. Any changes to the state should be fetched directly from Mission Planner/MAVLink.
    """

    def __init__(self, img_dir: str):
        
        if not os.path.exists(img_dir):
            print(
                f"Warning: specified camera output directory \"{img_dir}\" not found; Attempting to create one."
            )
            os.mkdir(img_dir)

        self.img_dir: str = img_dir

        self.mission_count: int = 0

        self.img_count: int = 0
        
        self.position: tuple[float, float, float] = (.0, .0, .0)

        self.waypoints: list[tuple[float, float]] = []

        self.significant_waypoints: list[tuple[float, float]] = []

        self.waypoint_counter: int = 0

        self.significant_counter: int = 0


    def next_waypoint(self):
        return self.waypoints[self.waypoint_counter]
    

    def next_significant(self):
        return self.significant_waypoints[self.significant_counter]
    
    def advance_waypoint(self):
        self.waypoint_counter += 1

    
    def advance_significant(self):
        self.significant_counter += 1


    def capture(self) -> Any:

        img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        img_dir = f"{self.img_dir.removesuffix('/')}/image{self.img_count}.jpg"

        cv2.imwrite(img_dir, img)
        self.img_count += 1

        return img_dir
