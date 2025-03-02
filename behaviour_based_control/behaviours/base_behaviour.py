from __future__ import annotations
from queue import PriorityQueue
from drone_package import Drone


class Behaviour:
    """
    Base type for all behaviors exhibited by the drone's behavior-based control.
    Derrived types include:
    * `behaviours.PathPlanning`
    * `behaviours.Takeoff`
    * `behaviours.PathFollowing`
    * `behaviours.Survey`
    * `behaviours.ProcessData`
    * `behaviours.ApproachRhino`
    * `behaviours.ApproachRhino`
    * `behaviours.DispatchPackage`
    * `behaviours.ReturnHome`
    """

    def __init__(self, code: int, priority: int, drone: Drone):
        """
        Expects an input of the behavior's code (ID), priority (importance) 
        and the reference to a `Drone` instance.
        *   `priority` defines the behavior's capacity to override behaviors of lower priority.
        *   `drone` is a reference to an instance of the `Drone` class—a wrapper class that 
            retrieves information regarding the UAV's state that are broadcasted using the MAVLink protocol.
        """
        self.code = code
        self.priority = priority
        self.drone = drone
        self.DISTANCE_THRESHOLD = 5.0   # meters

    def __lt__(self, other: "Behaviour"):
        return self.code < other.code

    def __str__(self):
        return "'" + type(self).__name__ + "'"

    def unroll(self) -> tuple[int, "Behaviour"]:
        """
        Returns the Behavior along with its priority. 
        It works as a decorator class for inserting a behavior within a 
        `queue.PriorityQueue` object, improving overall readability and 
        code aesthetic, e.g.:
        ```
        behavior_priority_queue.put(Behaviors.Takeoff(...).unroll())
        ```
        instead of writing
        ```
        takeoff_behavior = Behaviors.Takeoff(...)
        behavior_priority_queue.put(takeoff_behavior.priority, takeoff_behavior)
        ```
        """
        return self.priority, self

    def act(self, behavior_queue: PriorityQueue):
        """
        The main loop of the behavior's execution/ruleset. 
        A **priority queue** is demanded as input as new behaviors emerge during its execution. 
        ```
        """
        pass
