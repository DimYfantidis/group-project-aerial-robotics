from .base_behaviour import Behaviour
from .process_data import ProcessData
from drone_package import Drone
from queue import PriorityQueue


class Survey(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=4, priority=10, drone=drone)

    def act(self, behavior_queue: PriorityQueue):

        # TODO: Define data-logging frequency. 
        # TODO: Integrate the Raspberry Pi's camera scripts to save the captured images in the database.

        behavior_queue.put(ProcessData(self.drone).unroll())