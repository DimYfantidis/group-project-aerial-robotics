from database import db
from models import Mission, Image

def main():
    db.connect()
    db.create_tables([Mission, Image], safe=True)
    
    # Create a sample Mission record.
    mission = Mission.create(
        name="Fenswood Mission",
        altitude=50,
        zebras_count=100,
        rhino_lat=34.0522,
        rhino_lon=-118.2437,
        rhino_image="dataset/rhino.jpg",
        is_rhino_detected=True,
        takeoff_location_lat=34.0000,
        takeoff_location_lon=-118.0000,
        flight_region=[{"lat": 34.0, "lon": -118.0}, {"lat": 34.1, "lon": -118.1}],
        sensitive_area=[{"lat": 34.2, "lon": -118.2}],
        path_to_survey=[{"lat": 34.3, "lon": -118.3}],
        path_to_take_off=[{"lat": 34.4, "lon": -118.4}],
        survey_area=[{"lat": 34.5, "lon": -118.5}],
        survey_area_start={"lat": 34.6, "lon": -118.6},
        survey_area_end={"lat": 34.7, "lon": -118.7},
        processing_spots=[{"lat": 34.8, "lon": -118.8}]
    )
    
    image = Image.create(
        path="dataset/zebra.jpg", # TODO: Follow naming convention for storing images e.g. mission_id_image_id.png or mission_id_sequence_number.png
        lat=34.0522,
        lon=-118.2437,
        is_zebra=True,
        is_rhino=False,
        mission=mission  # Linking the image to the mission.
    )
    
    
    retrieved_mission = Mission.get(Mission.id == mission.id)
    print("Mission:", retrieved_mission.name)
    print("Number of Images:", retrieved_mission.images.count())
    
    db.close()

if __name__ == '__main__':
    main()
