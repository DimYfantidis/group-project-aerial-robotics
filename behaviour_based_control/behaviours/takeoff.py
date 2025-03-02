from .base_behaviour import Behaviour
from .path_following import PathFollowing
from drone_package import Drone
from queue import PriorityQueue


class Takeoff(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=2, priority=1, drone=drone)

    def act(self, behavior_queue: PriorityQueue):

        # TODO: Integrate MAVLink control scripts for initiating takeoff.
        # TODO: Request altitude of 50 meters above ground level (AGL).

        behavior_queue.put(PathFollowing(self.drone).unroll())
