from .base_behaviour import Behaviour
from .path_planning import PathPlanning
from queue import PriorityQueue
from drone_package import Drone


class StartMission(Behaviour):

    def __init__(self, drone: Drone):
            super().__init__(code=0, priority=-1, drone=drone)

    def act(self, behavior_queue: PriorityQueue):

        # TODO: Initialise and load all data (e.g. kml files).

        behavior_queue.put(PathPlanning(self.drone).unroll())
