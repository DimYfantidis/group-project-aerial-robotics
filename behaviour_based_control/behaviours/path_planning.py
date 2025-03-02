from .base_behaviour import Behaviour
from .takeoff import Takeoff
from drone_package import Drone
from queue import PriorityQueue


class PathPlanning(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=1, priority=0, drone=drone)

    def act(self, behavior_queue: PriorityQueue):
        
        # TODO: Create a sample Mission record.
        # TODO: Integrate the path planning scripts within this behaviour's main loop.
        
        behavior_queue.put(Takeoff(self.drone).unroll())
