import random
from shapely.geometry import Point

def random_point_in_polygon(poly, max_tries=1000):
    """
    Returns a random (lat, lon) within the given Shapely polygon `poly`.
    Shapely polygons use (lon, lat) order; this function returns (lat, lon).
    """
    minx, miny, maxx, maxy = poly.bounds
    for _ in range(max_tries):
        randx = random.uniform(minx, maxx)  # longitude
        randy = random.uniform(miny, maxy)  # latitude
        p = Point(randx, randy)
        if poly.contains(p):
            return (p.y, p.x)
    return None
