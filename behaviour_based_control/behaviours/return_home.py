from .base_behaviour import Behaviour
from drone_package import Drone
from queue import PriorityQueue


class ReturnHome(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=8, priority=8, drone=drone)

    def act(self, behavior_queue: PriorityQueue):
        
        # TODO: Calculate new set of waypoints from the drone's current position back to the start.
        # TODO: Integrate waypoint-following script. 

        # Clears the queue
        while not behavior_queue.empty():
            behavior_queue.get()

        # TODO: Send all databases to UDP-connected computer (client)
