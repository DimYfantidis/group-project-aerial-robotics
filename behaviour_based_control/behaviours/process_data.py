from .base_behaviour import Behaviour
from .approach_rhino import ApproachRhino
# from .survey import Survey  <----- leads to circular import! Placed within act() instead.
from drone_package import Drone
from queue import PriorityQueue


class ProcessData(Behaviour):

    def __init__(self, drone: Drone):
        super().__init__(code=5, priority=10, drone=drone)


    def act(self, behavior_queue: PriorityQueue):
        
        # TODO: Fetch previous survey data (images) from the databse. 
        # TODO: Create appropriate conditionals to branch either to ApproachRhino or Survey. 
        
        # TODO: If the rhino is observed in an entry then:
        # - log its position (in a shared variable)
        # - log the image ID
        # - keep processing the rest of the images

        from behaviours.survey import Survey
        # behavior_queue.put(Survey(self.drone).unroll())  
        pass