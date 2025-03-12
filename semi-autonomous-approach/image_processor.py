from ultralytics import YOLO
from ultralytics.engine.results import Results
from threading import Thread
from auto_capture import SAVE_DIR_ABS
from gpiar_db.models import Image, Mission, MissionStatus
from glob import glob
import numpy as np
import cv2 as cv
import math 


class ImageProcessor:

    class ImageResults:
        
        def __init__(self, yolo_result: Results, ca):
            
            self.class_names = yolo_result.names
            self.width = yolo_result.orig_shape[1]
            self.height = yolo_result.orig_shape[0]
            self.filepath = yolo_result.path

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
                    'up' : u, 
                    'down' : d, 
                    'left' : l,
                    'right' : r
                })
                self.obj_centres.append((
                    (u + d) / 2.0,
                    (l + r) / 2.0
                ))


    def __init__(self, model_path: str, visible_ground_dims: tuple[float, float]):
        self.model = YOLO(model_path)
        self.ground_width, self.ground_length = visible_ground_dims
        self.mission: Mission = Mission.get(Mission.status == MissionStatus.ACTIVE)
        # self.thread = None

    
    def remove_distortion(camMatrix, distCoeff, img_samples_paths: list[str]) -> list[np.ndarray]:

        img_samples = [cv.imread(im_path) for im_path in img_samples_paths]
        img_undist = []

        for img in img_samples:

            height, width = img.shape[:2]

            camMatrixNew, roi = cv.getOptimalNewCameraMatrix(camMatrix, distCoeff, (width, height), 1, (width, height))
            img_undist.append(
                cv.undistort(img, camMatrix, distCoeff, None, camMatrixNew)
            )
        
        return img_undist


    def process_and_save_images(self) -> None:

        unprocessed_image_paths = []

        for img_path in glob("./capture-images/*.png"):

            img: Image = Image.get(Image.path == img_path)

            if img.is_processed:
                continue

            unprocessed_image_paths.append(img.path)
            
            img.update(
                is_processed=True
            )


        results: list[Results] = self.model(unprocessed_image_paths)

        n_zebras = 0

        for result in results:

            image_result = ImageProcessor.ImageResults(result)

            img: Image = Image.get(
                Image.path == image_result.filepath
            )

            drone_lat = img.lat
            drone_lon = img.lon
            drone_yaw = img.yaw

            is_zebra = False

            is_rhino = False

            zebra_locations = []

            rhino_lat = None
            rhino_lon = None
            rhino_image = None

            # Camera's up vector is at the opposite direction of the drone's orientation.
            camera_yaw = np.deg2rad(drone_yaw - 180.0)
            sin_yaw = math.sin(camera_yaw)
            cos_yaw = math.cos(camera_yaw)

            rotation_matrix = np.array([
                [cos_yaw, -sin_yaw],
                [sin_yaw, cos_yaw]
            ])

            for i in range(image_result.n_animals):

                # Compute the model estimation's x and z components.
                model_estimation = np.matmul(rotation_matrix, np.array([
                    [(self.ground_length / 2) * image_result.obj_centres[i][0]],
                    [(self.ground_width / 2) * image_result.obj_centres[i][1]]
                ]))

                model_geo_coords = np.array([
                    drone_lat + model_estimation[0] / 111194.92664455873,
                    drone_lon + model_estimation[1] / (111194.92664455873 * np.cos(np.deg2rad(drone_lat)))
                ])

                if image_result.animals[i] == 'zebra':
                    zebra_locations.append({
                        "lat" : model_geo_coords[0],
                        "lon" : model_geo_coords[1]
                    })
                    n_zebras += 1
                    is_zebra = True

                elif image_result.animals[i] == 'rhinoceros':
                    is_rhino = True
                    rhino_lat = model_geo_coords[0]
                    rhino_lon = model_geo_coords[1]
                    rhino_image = image_result.filepath


            if is_rhino: 
                self.mission.update(
                    rhino_lat=rhino_lat,
                    rhino_lon=rhino_lon,
                    rhino_image=rhino_image
                )

            img.update(
                is_zebra=is_zebra,
                is_rhino=is_rhino,
                zebra_locations=zebra_locations
            )

        self.mission.update(
            zebras_count=self.mission.zebras_count+n_zebras
        )


    # def start(self, image_paths: list[str]) -> None:

    #     self.thread = Thread(target=self.process_and_save_images)
    #     self.thread.start()

