# main.py
from kml_parser import KMLParser
from geometry_utils import random_point_in_polygon
from path_planner import PathPlanner
from map_generator import MapGenerator
from drone import connect_vehicle, set_geofence, upload_mission
from shapely.geometry import Polygon, Point
import numpy as np

def main():
    # Parse KML file
    kml_file = 'AENGM0074 2025 geolocations_new.kml'
    attrs = KMLParser.parse_kml(kml_file)

    # Extract Take-Off location
    takeoff_str = attrs["Take-Off Location"]
    lon_tk, lat_tk, *_ = takeoff_str.split(',')
    lon_tk, lat_tk = float(lon_tk), float(lat_tk)

    # Build Sensitive Area polygon (with a buffer)
    sens_coords = []
    for pair in attrs["Sensitive Area"].split():
        lon, lat, *_ = pair.split(',')
        sens_coords.append((float(lon), float(lat)))
    sensitive_polygon = Polygon(sens_coords).buffer(0.0000001)

    # Build Survey Area polygon
    survey_coords = []
    for pair in attrs["Survey Area"].split():
        lon, lat, *_ = pair.split(',')
        survey_coords.append((float(lon), float(lat)))
    survey_polygon = Polygon(survey_coords)

    # Build Flight Region polygon
    flight_coords = []
    for pair in attrs["Flight Region"].split():
        lon, lat, *_ = pair.split(',')
        flight_coords.append((float(lon), float(lat)))
    flight_polygon = Polygon(flight_coords)

    # Determine approach corner (bottom-left of survey area)
    lon_min, lat_min, lon_max, lat_max = survey_polygon.bounds
    approach_corner = (lat_min, lon_min)

    # Compute grid bounds for approach path planning
    all_lats = [lat_tk, lat_min, lat_max] + [p[1] for p in sens_coords] + [p[1] for p in flight_coords]
    all_lons = [lon_tk, lon_min, lon_max] + [p[0] for p in sens_coords] + [p[0] for p in flight_coords]
    min_lat_grid = min(all_lats) - 0.001
    max_lat_grid = max(all_lats) + 0.001
    min_lon_grid = min(all_lons) - 0.001
    max_lon_grid = max(all_lons) + 0.001
    resolution = 0.0001

    # Create a PathPlanner instance
    planner = PathPlanner(flight_polygon, sensitive_polygon, resolution=resolution)

    # Plan approach path (from Take-Off to approach corner)
    lat_steps = int((max_lat_grid - min_lat_grid) / resolution) + 1
    lon_steps = int((max_lon_grid - min_lon_grid) / resolution) + 1
    grid = np.zeros((lat_steps, lon_steps), dtype=int)
    for i in range(lat_steps):
        for j in range(lon_steps):
            lat_cell = min_lat_grid + i * resolution
            lon_cell = min_lon_grid + j * resolution
            pt = Point(lon_cell, lat_cell)
            if not flight_polygon.contains(pt):
                grid[i, j] = 1
            elif sensitive_polygon.contains(pt):
                grid[i, j] = 1

    start_idx = planner.latlon_to_grid(lat_tk, lon_tk, min_lat_grid, min_lon_grid)
    goal_idx = planner.latlon_to_grid(approach_corner[0], approach_corner[1], min_lat_grid, min_lon_grid)
    path_indices = planner.a_star_search(grid, start_idx, goal_idx)
    if path_indices is None:
        print("No approach path found.")
        return
    raw_approach_path = [planner.grid_to_latlon(i, j, min_lat_grid, min_lon_grid) for (i, j) in path_indices]
    approach_path = planner.smooth_path(raw_approach_path)

    # Generate rotated zigzag coverage for the survey area
    coverage_path = planner.generate_rotated_zigzag(survey_polygon, spacing=0.00009, inner_margin=0.000001)
    if not coverage_path:
        print("No coverage path generated.")
        return
    # Reverse coverage if needed
    def latlon_distance(a, b):
        return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5
    if latlon_distance(approach_corner, coverage_path[0]) > latlon_distance(approach_corner, coverage_path[-1]):
        coverage_path.reverse()
    coverage_path[0] = approach_corner
    if len(coverage_path) >= 2:
        coverage_path = coverage_path[:-2]
    if approach_path[-1] == approach_corner:
        final_path_coords = approach_path + coverage_path[1:]
    else:
        final_path_coords = approach_path + coverage_path

    # # Select a random Rhino location within the survey area
    from geometry_utils import random_point_in_polygon
    rhino_location = random_point_in_polygon(survey_polygon)
    if rhino_location is None:
        print("Could not get random Rhino location in the Survey Area!")
        return
    print("Random Rhino Location:", rhino_location)

    # # Check Rhino validity
    if not flight_polygon.contains(Point(rhino_location[1], rhino_location[0])):
        print("WARNING: Rhino location is outside the Flight Region!")
    if sensitive_polygon.contains(Point(rhino_location[1], rhino_location[0])):
        print("WARNING: Rhino location is inside the Sensitive Area!")

    # # Plan path from Rhino to Take-Off
    rhino_takeoff_path = planner.plan_path_from_x_to_takeoff(rhino_location, (lat_tk, lon_tk))
    if rhino_takeoff_path is None:
        print("No valid path found from Rhino to Takeoff.")
    else:
        print("--- Rhino to Takeoff Waypoints ---")
        for wp in rhino_takeoff_path:
            print(wp)

    # Create the map (centered on overall grid bounds)
    center = (0.5 * (min_lat_grid + max_lat_grid), 0.5 * (min_lon_grid + max_lon_grid))
    map_gen = MapGenerator(center, zoom_start=16)

    # Add polygons for Sensitive, Flight, and Survey areas
    map_gen.add_polygon([(lat, lon) for lon, lat in sens_coords],
                        color="red", tooltip="Sensitive Area", fill=True, fill_opacity=0.4)
    map_gen.add_polygon([(lat, lon) for lon, lat in flight_coords],
                        color="green", tooltip="Flight Region", fill=False, weight=3)
    map_gen.add_polygon([(lat, lon) for lon, lat in survey_coords],
                        color="blue", tooltip="Survey Area", fill=True, fill_opacity=0.2)

    # Add the mission path (approach + coverage)
    map_gen.add_polyline(final_path_coords, color="darkblue", tooltip="Zigzag Coverage Path")

    # Add markers: Take-Off, Rhino (random), and Survey centroid
    map_gen.add_marker([lat_tk, lon_tk], "Take-Off Location", "green", icon="rocket")
    # map_gen.add_marker(rhino_location, "Rhino Location (random in Survey)", "purple", icon="info-sign")
    survey_centroid = survey_polygon.centroid
    map_gen.add_marker([survey_centroid.y, survey_centroid.x], "Survey (Centroid)", "blue", icon="flag")

    # Add markers for processing spots (every second point in coverage) skipping the first one
    for i in range(1, len(coverage_path), 2):
        if i == 1:
            continue  # Delete the first processing spot
        marker_text = f"Processing Spot #{i}"
        map_gen.add_marker(coverage_path[i], marker_text, "orange", icon="info-sign")

    # # Add Rhino-to-Takeoff path if available
    if rhino_takeoff_path:
        map_gen.add_polyline(rhino_takeoff_path, color="purple", tooltip="Rhino to Takeoff Path", weight=6)

    # Add legend
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px;
        background-color: white; 
        border:2px solid grey; 
        z-index:9999; 
        font-size:14px;
        padding: 10px;
    ">
    <b>Legend</b><br>
    <span style="color:green;">&#9679;</span> Take-Off Location<br>
    <span style="color:purple;">&#9679;</span> Rhino Location (random)<br>
    <span style="color:blue;">&#9679;</span> Survey (Centroid)<br>
    <span style="color:red;">&#9679;</span> Sensitive Area<br>
    <span style="color:green;">&#9646;</span> Flight Region<br>
    <span style="color:blue;">&#9646;</span> Survey Area Boundary<br>
    <span style="color:darkblue;">&#9646;</span> Zigzag Coverage Path<br>
    <span style="color:orange;">&#9679;</span> Processing Spot<br>
    <span style="color:purple;">&#9646;</span> Rhino to Takeoff Path<br>
    </div>
    {% endmacro %}
    """
    map_gen.add_legend(legend_html)
    map_gen.fit_bounds()
    map_gen.save("path_planning_map.html")
    print("Map saved to 'path_planning_map.html'.")

    # Print all key locations
    print("\n--- Locations ---")
    print("Take-Off Location:", (lat_tk, lon_tk))
    print("Flight Region Coordinates:")
    for lon, lat in flight_coords:
        print((lat, lon))
    print("Sensitive Area Coordinates:")
    for lon, lat in sens_coords:
        print((lat, lon))
    print("Survey Area Coordinates:")
    for lon, lat in survey_coords:
        print((lat, lon))
    print("Processing Spots:")
    for i in range(1, len(coverage_path), 2):
        if i == 1:
            continue  # first processing spot skipped
        print(coverage_path[i])
    print("Random Rhino Location:", rhino_location)

    # Upload mission to drone
    # vehicle = connect_vehicle("tcp:127.0.0.1:14550")
    # set_geofence(vehicle, flight_coords, fence_altitude=50)
    # waypoints = [(lat, lon, 10) for lat, lon in final_path_coords]
    # upload_mission(vehicle, waypoints)
    # print("Mission uploaded to vehicle.")

if __name__ == '__main__':
    main()
