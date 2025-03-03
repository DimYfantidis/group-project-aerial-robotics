from .base_behaviour import Behaviour
from .survey import Survey
from drone_package import Drone
from queue import PriorityQueue


class PathFollowing(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=3, priority=2, drone=drone)

    def act(self, behavior_queue: PriorityQueue):
        
        # TODO: Integrate waypoint-following script. 

        behavior_queue.put(Survey(self.drone).unroll())

