from .base_behaviour import Behaviour
from .return_home import ReturnHome
from drone_package import Drone
from queue import PriorityQueue


class DispatchPackage(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=7, priority=9, drone=drone)

    def act(self, behavior_queue: PriorityQueue):

        # TODO: Define level of autonomy (LOA).
        # TODO: Implement main loop for dispatching the sensor package next to the rhino based on define LOA. 
        
        # This behaviour is triggered right after `behavior.ApproachRhino` finishes and, thus, 
        # the drone is already situated in the right spot. 

        behavior_queue.put(ReturnHome(self.drone).unroll())
