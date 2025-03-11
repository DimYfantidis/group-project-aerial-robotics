from ultralytics import YOLO
from ultralytics.engine.results import Results
from threading import Thread
from auto_capture import SAVE_DIR_ABS
from gpiar_db.models import Image
from glob import glob
import cv2 as cv 


class ImageProcessor:

    class ImageResults:
        
        def __init__(self, yolo_result: Results):
            
            self.class_names = yolo_result.names
            self.width = yolo_result.orig_shape[1]
            self.height = yolo_result.orig_shape[0]
            self.filepath = yolo_result.path

            self.animals = [self.class_names[ID] for ID in yolo_result.boxes.cls.cpu().numpy()]
            self.confidences = [conf for conf in yolo_result.boxes.conf.cpu().numpy()]
            self.bboxes = []

            boxes = yolo_result.boxes.xyxy.cpu().numpy()

            img_mid = (self.width / 2, self.height / 2)

            for i in range(len(self.animals)):
                
                l = 2 * ((boxes[i][0] - img_mid[0]) / self.width)
                r = 2 * ((boxes[i][2] - img_mid[0]) / self.width)
                u = 2 * (((self.height - boxes[i][1]) - img_mid[1]) / self.height)
                d = 2 * (((self.height - boxes[i][3]) - img_mid[1]) / self.height)

                self.bboxes.append({
                    'up' : u, 
                    'down' : d, 
                    'left' : l,
                    'right' : r
                })


    def __init__(self, model_path: str):
        self.model = YOLO(model_path)
        self.thread = None


    def process_and_save_images(self, image_paths: list[str]) -> None:

        unprocessed_image_paths = []

        for img_path in glob("./capture-images/*.png"):

            img: Image = Image.get(Image.path == img_path)

            if img.is_processed:
                continue

            unprocessed_image_paths.append(img.path)


        results: list[Results] = self.model(unprocessed_image_paths)

        for result in results:

            image_result = ImageProcessor.ImageResults(result)

            

            




    def start(self, image_paths: list[str]) -> None:

        self.thread = Thread(target=self.process_and_save_images)
        self.thread.start()


if __name__ == '__main__':

    processor = ImageProcessor('./yolo_model/best.pt')

    print('> Loaded YOLOv8')

    processor.process_images(['./yolo_model/sample.png'])
