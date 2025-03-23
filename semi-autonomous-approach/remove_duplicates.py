import json
import logging
from geopy import distance
from image import Image
from database import db
from glob import glob
import os

def remove_duplicates(dir_abs_path: str) ->  list[dict[str, float]]:

    zebra_locations = []
    total_zebras = 0

    for img_path in glob(os.path.join(dir_abs_path, "*.png")):
        # Convert the absolute path to a relative path from the current working directory.
        relative_path = os.path.relpath(img_path, os.getcwd())
        # Normalize the relative path to ensure a consistent format.
        relative_path = os.path.normpath(relative_path)

        image_id = relative_path.split(os.sep)[-1].removesuffix('.png')

        img: Image = Image.select().where(
            (Image.id == image_id) & (Image.is_processed == True)
        ).first()

        if img is None:
            continue

        if img.is_processed:
            continue

        for loc in json.loads(img.zebra_locations):

            zebra_locations.append((loc['lat'], loc['lon']))

    is_duplicate = [False for _ in range(len(zebra_locations))]

    THRESHOLD_DUPLICATE = 0.5  # meters

    for i in range(len(zebra_locations)):

        for j in range(i+1, len(zebra_locations), 1):

            if is_duplicate[i]:
                continue

            if distance(zebra_locations[i], zebra_locations[j]).meters < THRESHOLD_DUPLICATE:
                is_duplicate[j] = True

    zebra_locations_filtered = [
        {
            'lat': loc[0],
            'lon': loc[1]
        }
        for loc, dup in zip(zebra_locations, is_duplicate)
        if not dup
    ]

    logging.info(
        f"Found {len(zebra_locations) - len(zebra_locations_filtered)} duplicate zebra entries; Returning filtered results.")

    return zebra_locations_filtered


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    db.connect()

    zebras = remove_duplicates("./capture-images")