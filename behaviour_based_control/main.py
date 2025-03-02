import behaviours

from drone_package import Drone
from queue import PriorityQueue


if __name__ == '__main__':
    # Priority queue responsible for the behaviour-based control of the UAV.
    behaviors_queue = PriorityQueue()

    # Instantiate Drone API
    drone = Drone(img_dir='./images/')

    behaviors_queue.put(
        # Initiate Fenswood expedtion for Autonomous Wildlife Monitoring​.
        # The entire expedition—from start to finish—will be referred to as "Mission".
        behaviours.StartMission(drone=drone).unroll()
    )

    # Behaviour-based control loop
    while not behaviors_queue.empty():

        priority, task = behaviors_queue.get()

        priority: int = priority
        task: behaviours.Behaviour = task

        print(f"Processing {task} with priority {priority}")
        task.act(behaviors_queue)
