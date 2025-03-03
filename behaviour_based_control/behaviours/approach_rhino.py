from .base_behaviour import Behaviour
from .dispatch_package import DispatchPackage
from drone_package import Drone
from queue import PriorityQueue


class ApproachRhino(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=6, priority=9, drone=drone)

    def act(self, behavior_queue: PriorityQueue):

        # TODO: Retrieve rhino's position from the database. 
        # TODO: Approach it by applying dead-reckoning navigation (https://en.wikipedia.org/wiki/Dead_reckoning).
        
        behavior_queue.put(DispatchPackage(self.drone).unroll())
