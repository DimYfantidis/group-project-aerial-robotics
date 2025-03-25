import numpy as np
import math 
from include.pid import PID


# Define the boundary values.
u = 30.0
d = -30.0
l = -30.0
r = 30.0

up_pid = PID(.01, .0, .0)
right_pid = PID(.01, .0, .0)


if __name__ == '__main__':

    while True:
        # Create the 3D vectors using NumPy arrays.
        p1 = np.array([u, 0, l])
        p2 = np.array([u, 0, r])
        p3 = np.array([d, 0, r])
        p4 = np.array([d, 0, l])


        height = 50.0

        camera_cartesian = np.array([0, height, 0])
        camera_geo_coords = np.zeros((lat, height, lon))

        v1 = p1 - camera_cartesian
        v2 = p2 - camera_cartesian
        v3 = p3 - camera_cartesian
        v4 = p4 - camera_cartesian


        # Compute horizontal field of view (HFOV) in degrees
        HFOV = math.degrees(
            math.acos(
                np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            )
        )

        # Compute vertical field of view (VFOV) in degrees
        VFOV = math.degrees(
            math.acos(
                np.dot(v2, v3) / (np.linalg.norm(v2) * np.linalg.norm(v3))
            )
        )

        print(f"\rHFOV : VFOV = {HFOV} : {VFOV}", end='')

        u += up_pid.update(34.0, VFOV)
        r += right_pid.update(45.0, HFOV)

        # Compute the horizontal and vertical differences.
        diff_horz = p1 - p2
        diff_vert = p3 - p2

        # Compute the lengths (magnitudes) of these difference vectors.
        diff_horz_len = np.linalg.norm(diff_horz)
        diff_vert_len = np.linalg.norm(diff_vert)


        # Define the dummy object percentage offsets.
        dummy_obj_horz_percentage = -0.3
        dummy_obj_vert_percentage = 0.2

        # Assume diff_horz_len, diff_vert_len, and camera_pos are defined previously.
        # For example:
        # diff_horz_len = 60.0
        # diff_vert_len = 40.0
        # camera_pos = np.array([10.0, 0.0, 20.0])

        # Initialize the model estimation vector with zeros.
        model_estimation = np.zeros(3)

        # Compute the model estimation's x and z components.
        model_estimation[0] = (diff_vert_len / 2) * dummy_obj_vert_percentage
        model_estimation[2] = (diff_horz_len / 2) * dummy_obj_horz_percentage

        model_geo_coords = np.array([
            camera_geo_coords[0] + model_estimation[0] / 111194.44,
            np.nan,
            camera_geo_coords[2] + model_estimation[2] / (111194.44 * np.cos(np.deg2rad(camera_geo_coords[0])))
        ])
