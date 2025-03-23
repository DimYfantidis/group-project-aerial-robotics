from ultralytics import YOLO
from ultralytics.engine.results import Results
from mission import Mission, MissionStatus
from image import Image
from database import db
from glob import glob
import numpy as np
import cv2 as cv
import logging
import math
import os


class ImageProcessor:

    class ImageResults:
        def __init__(self, yolo_result: Results, filepath: str):
            logging.getLogger("peewee").setLevel(logging.WARNING)
            self.class_names = yolo_result.names
            self.width = yolo_result.orig_shape[1]
            self.height = yolo_result.orig_shape[0]
            self.filepath = filepath

            self.animals = [self.class_names[ID] for ID in yolo_result.boxes.cls.cpu().numpy()]
            self.confidences = [conf for conf in yolo_result.boxes.conf.cpu().numpy()]
            self.bboxes = []
            self.n_animals = len(self.animals)
            boxes = yolo_result.boxes.xyxy.cpu().numpy()
            self.obj_centres = []
            img_mid = (self.width / 2, self.height / 2)

            for i in range(len(self.animals)):
                l = 2.0 * ((boxes[i][0] - img_mid[0]) / self.width)
                r = 2.0 * ((boxes[i][2] - img_mid[0]) / self.width)
                u = 2.0 * (((self.height - boxes[i][1]) - img_mid[1]) / self.height)
                d = 2.0 * (((self.height - boxes[i][3]) - img_mid[1]) / self.height)

                self.bboxes.append({
                    'up': u,
                    'down': d,
                    'left': l,
                    'right': r
                })
                self.obj_centres.append(((u + d) / 2.0, (l + r) / 2.0))

    def __init__(self, model_path: str, visible_ground_dims: tuple[float, float]):
        self.model = YOLO(model_path)
        self.ground_width, self.ground_length = visible_ground_dims
        self.mission: Mission = Mission.get(Mission.status == MissionStatus.ACTIVE)
        logging.info("Instantiated ImageProcessor Successfully")
        # self.thread = None

    def remove_distortion(self, cam_matrix: np.ndarray, dist_coeff: np.ndarray, img_samples_paths: list[str], save_corrected: bool = False) -> list[np.ndarray]:
        img_samples = [cv.imread(im_path) for im_path in img_samples_paths]
        img_undist = []

        for img in img_samples:
            height, width = img.shape[:2]
            camMatrixNew, roi = cv.getOptimalNewCameraMatrix(cam_matrix, dist_coeff, (width, height), 1, (width, height))
            img_undist.append(cv.undistort(img, cam_matrix, dist_coeff, None, camMatrixNew))

        if save_corrected:
            for corrected, img_path in zip(img_undist, img_samples_paths):
                cv.imwrite(filename=img_path.removesuffix('.png') + '-corrected.png', img=corrected)

        logging.info(f"Removed distortion from {len(img_samples)} images")
        return img_undist

    def process_and_save_images(self, dir_abs_path: str) -> None:
        # Gather unprocessed image objects and their paths
        unprocessed_images = []
        unprocessed_image_paths = []

        for img_path in glob(os.path.join(dir_abs_path, "*.png")):
            relative_path = os.path.relpath(img_path, os.getcwd())
            relative_path = os.path.normpath(relative_path)
            image_id = relative_path.split(os.sep)[-1].removesuffix('.png')

            img: Image = Image.select().where(
                (Image.id == image_id) & (Image.is_processed == False)
            ).first()
            if not img:
                continue

            unprocessed_images.append(img)
            unprocessed_image_paths.append(img.path)

        if not unprocessed_image_paths:
            logging.info('No unprocessed images found. Exiting `ImageProcessor.process_and_save_images`')
            return

        camera_parameters = np.load("./yolo_model/calibration.npz")
        camera_matrix, dist_coeff = camera_parameters['camMatrix'], camera_parameters['distCoeff']

        corrected_images = self.remove_distortion(camera_matrix, dist_coeff, unprocessed_image_paths)
        results: list[Results] = self.model(corrected_images)
        logging.info("Calculated predictions for the sampled images")

        total_zebra_count = 0

        # Process each image result and update the corresponding image record
        for index, result in enumerate(results):
            image_result = ImageProcessor.ImageResults(result, unprocessed_image_paths[index])
            logging.info(f"Processing image #{index+1}: {image_result.filepath}")

            # Retrieve the image object from our collected list
            img = unprocessed_images[index]
            drone_lat = img.lat
            drone_lon = img.lon
            drone_yaw = img.yaw

            # Calculate camera yaw (opposite of drone orientation)
            camera_yaw = np.deg2rad(drone_yaw - 180.0)
            sin_yaw = math.sin(camera_yaw)
            cos_yaw = math.cos(camera_yaw)

            rotation_matrix = np.array([
                [cos_yaw, -sin_yaw],
                [sin_yaw,  cos_yaw]
            ])

            # Initialize per-image detection variables
            is_zebra = False
            zebra_locations = []
            is_rhino = False
            rhino_lat = None
            rhino_lon = None
            rhino_image = None

            if image_result.n_animals == 0:
                logging.info(f"No animals found in image: {unprocessed_image_paths[index]}")
            else:
                # Process each detected animal using a separate loop variable 'j'
                for j in range(image_result.n_animals):
                    model_estimation = np.matmul(rotation_matrix, np.array([
                        [(self.ground_length / 2) * image_result.obj_centres[j][0]],
                        [(self.ground_width / 2) * image_result.obj_centres[j][1]]
                    ]))

                    model_geo_coords = np.array([
                        drone_lat + model_estimation[0] / 111194.92664455873,
                        drone_lon + model_estimation[1] / (111194.92664455873 * np.cos(np.deg2rad(drone_lat)))
                    ])

                    if image_result.animals[j] == 'zebra':
                        logging.info("> Found Zebra at (%+6.2f%%, %+6.2f%%)" %
                                     (100 * image_result.obj_centres[j][0], 100 * image_result.obj_centres[j][1]))
                        zebra_locations.append({
                            "lat": float(model_geo_coords[0][0]),
                            "lon": float(model_geo_coords[1][0])
                        })
                        total_zebra_count += 1
                        is_zebra = True

                    elif image_result.animals[j] == 'rhinoceros':
                        is_rhino = True
                        rhino_lat, = model_geo_coords[0].ravel()
                        rhino_lon, = model_geo_coords[1].ravel()
                        rhino_lat = float(rhino_lat)
                        rhino_lon = float(rhino_lon)
                        rhino_image = image_result.filepath

            if is_rhino:
                logging.info(f"Rhino found at ({rhino_lat:.5f}, {rhino_lon:.5f}) in image {rhino_image}")
                logging.info(f"{rhino_lat:.5f};{rhino_lon:.5f};50")
                self.mission.update(
                    rhino_lat=rhino_lat,
                    rhino_lon=rhino_lon,
                    rhino_image=rhino_image
                ).execute()

            # Update the image record with detection results and mark it as processed
            img.is_zebra = is_zebra
            img.is_rhino = is_rhino
            img.zebra_locations = zebra_locations
            img.is_processed = True
            img.save()

        # Update the mission with the cumulative zebra count
        self.mission.update(
            zebras_count=self.mission.zebras_count + total_zebra_count
        ).where(Mission.status == MissionStatus.ACTIVE).execute()

if __name__ == '__main__':

    logging.basicConfig(
        # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        level=logging.DEBUG,
        # Log message format
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    db.connect()

    processor = ImageProcessor(
        './yolo_model/best.pt', visible_ground_dims=(43.665521, 33.360636))

    processor.process_and_save_images(
        os.path.abspath("./yolo_model")
    )

    db.close()
