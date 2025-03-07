import heapq, math, numpy as np
from shapely.geometry import Point, LineString
from shapely.affinity import rotate, translate

class PathPlanner:
    def __init__(self, flight_polygon, sensitive_polygon, resolution=0.0001, margin=0.001):
        self.flight_polygon = flight_polygon
        self.sensitive_polygon = sensitive_polygon
        self.resolution = resolution
        self.margin = margin

    def latlon_to_grid(self, lat, lon, min_lat, min_lon):
        i = int((lat - min_lat) / self.resolution)
        j = int((lon - min_lon) / self.resolution)
        return (i, j)

    def grid_to_latlon(self, i, j, min_lat, min_lon):
        lat = min_lat + i * self.resolution
        lon = min_lon + j * self.resolution
        return (lat, lon)

    def heuristic(self, a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def a_star_search(self, grid, start, goal):
        rows, cols = grid.shape
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                    if grid[neighbor] == 0:
                        tentative_g = g_score[current] + 1
                        if neighbor not in g_score or tentative_g < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g
                            f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                            if neighbor not in [item[1] for item in open_set]:
                                heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def can_travel_straight(self, start_latlon, end_latlon):
        start_lat, start_lon = start_latlon
        end_lat, end_lon = end_latlon
        line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
        inside_flight = self.flight_polygon.covers(line)
        intersects_sensitive = line.intersects(self.sensitive_polygon)
        return inside_flight and not intersects_sensitive

    def smooth_path(self, raw_path):
        n = len(raw_path)
        if n < 2:
            return raw_path
        smoothed = []
        i = 0
        while i < n:
            smoothed.append(raw_path[i])
            if i == n - 1:
                break
            best_j = i + 1
            j = i + 2
            while j < n:
                if self.can_travel_straight(raw_path[i], raw_path[j]):
                    best_j = j
                    j += 1
                else:
                    break
            i = best_j
        return smoothed

    def generate_rotated_zigzag(self, survey_polygon, spacing=0.0002, inner_margin=0.0):
        if survey_polygon.is_empty:
            return []
        mrr = survey_polygon.minimum_rotated_rectangle
        if mrr.is_empty:
            return []
        corners = list(mrr.exterior.coords)
        if len(corners) < 2:
            return []
        origin_global = corners[0]  # (lon, lat)
        dx = corners[1][0] - corners[0][0]
        dy = corners[1][1] - corners[0][1]
        if math.hypot(dx, dy) < 1e-9:
            return []
        angle_deg = math.degrees(math.atan2(dy, dx))
        shifted_poly = translate(survey_polygon, xoff=-origin_global[0], yoff=-origin_global[1])
        local_poly = rotate(shifted_poly, -angle_deg, origin=(0, 0), use_radians=False)
        minx, miny, maxx, maxy = local_poly.bounds
        if (maxx - minx) < 1e-9 or (maxy - miny) < 1e-9:
            return []
        minx += inner_margin
        maxx -= inner_margin
        miny += inner_margin
        maxy -= inner_margin
        if minx > maxx or miny > maxy:
            return []
        coverage_path = []
        x = minx
        col_index = 0
        while x <= maxx + 1e-12:
            if col_index % 2 == 0:
                line_local = LineString([(x, miny), (x, maxy)])
            else:
                line_local = LineString([(x, maxy), (x, miny)])
            line_global = rotate(line_local, angle_deg, origin=(0, 0), use_radians=False)
            line_global = translate(line_global, xoff=origin_global[0], yoff=origin_global[1])
            coords_global = [(pt[1], pt[0]) for pt in line_global.coords]  # (lat, lon)
            if coverage_path and coverage_path[-1] == coords_global[0]:
                coverage_path.extend(coords_global[1:])
            else:
                coverage_path.extend(coords_global)
            x += spacing
            col_index += 1
        return coverage_path

    def plan_path_from_x_to_takeoff(self, start, takeoff):
        # Build bounding box for grid
        all_lats = [start[0], takeoff[0]]
        all_lons = [start[1], takeoff[1]]
        for lon, lat in self.flight_polygon.exterior.coords:
            all_lats.append(lat)
            all_lons.append(lon)
        for lon, lat in self.sensitive_polygon.exterior.coords:
            all_lats.append(lat)
            all_lons.append(lon)
        min_lat = min(all_lats) - self.margin
        max_lat = max(all_lats) + self.margin
        min_lon = min(all_lons) - self.margin
        max_lon = max(all_lons) + self.margin
        lat_steps = int((max_lat - min_lat) / self.resolution) + 1
        lon_steps = int((max_lon - min_lon) / self.resolution) + 1
        grid = np.zeros((lat_steps, lon_steps), dtype=int)
        for i in range(lat_steps):
            for j in range(lon_steps):
                lat_cell = min_lat + i * self.resolution
                lon_cell = min_lon + j * self.resolution
                pt = Point(lon_cell, lat_cell)
                if not self.flight_polygon.contains(pt):
                    grid[i, j] = 1
                elif self.sensitive_polygon.contains(pt):
                    grid[i, j] = 1
        start_idx = self.latlon_to_grid(start[0], start[1], min_lat, min_lon)
        goal_idx = self.latlon_to_grid(takeoff[0], takeoff[1], min_lat, min_lon)
        path_indices = self.a_star_search(grid, start_idx, goal_idx)
        if path_indices is None:
            return None
        raw_path = [self.grid_to_latlon(i, j, min_lat, min_lon) for (i, j) in path_indices]
        return self.smooth_path(raw_path)
