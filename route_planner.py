import math
import json
import os
from typing import List, Tuple, Optional

class Point:
    def __init__(self, lat: float, lng: float):
        self.lat = lat
        self.lng = lng
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.lat - other.lat)**2 + (self.lng - other.lng)**2) * 111
    
    def __repr__(self):
        return f"Point({self.lat:.6f}, {self.lng:.6f})"

class Obstacle:
    def __init__(self, name: str, coords: List[Tuple[float, float]], height: float = 50.0):
        self.name = name
        self.coords = coords
        self.height = height
        self.points = [Point(lat, lng) for lat, lng in coords]
    
    def contains_point(self, point: Point, buffer: float = 0.0001) -> bool:
        return self._point_in_polygon(point, buffer)
    
    def _point_in_polygon(self, point: Point, buffer: float) -> bool:
        n = len(self.points)
        inside = False
        for i in range(n):
            j = (i + 1) % n
            xi, yi = self.points[i].lat, self.points[i].lng
            xj, yj = self.points[j].lat, self.points[j].lng
            
            if ((yi > point.lat) != (yj > point.lat)):
                x_intersect = (point.lat - yi) * (xj - xi) / (yj - yi) + xi
                if point.lng < x_intersect + buffer:
                    inside = not inside
        return inside
    
    def distance_to_segment(self, p1: Point, p2: Point) -> float:
        return min(
            min(p.distance_to(p1), p.distance_to(p2))
            for p in self.points
        )
    
    def get_centroid(self) -> Point:
        if not self.points:
            return Point(0, 0)
        avg_lat = sum(p.lat for p in self.points) / len(self.points)
        avg_lng = sum(p.lng for p in self.points) / len(self.points)
        return Point(avg_lat, avg_lng)

class Waypoint:
    def __init__(self, lat: float, lng: float, altitude: float = 100.0, speed: float = 15.0, name: str = ""):
        self.lat = lat
        self.lng = lng
        self.altitude = altitude
        self.speed = speed
        self.name = name or f"WP{id(self)}"
    
    def to_dict(self):
        return {
            'lat': self.lat,
            'lng': self.lng,
            'altitude': self.altitude,
            'speed': self.speed,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            lat=data['lat'],
            lng=data['lng'],
            altitude=data.get('altitude', 100.0),
            speed=data.get('speed', 15.0),
            name=data.get('name', '')
        )

class RoutePlanner:
    def __init__(self):
        self.waypoints: List[Waypoint] = []
        self.obstacles: List[Obstacle] = []
        self.safety_distance = 0.0002
        self.uav_altitude = 100.0
    
    def set_uav_altitude(self, altitude: float):
        self.uav_altitude = altitude
    
    def add_waypoint(self, lat: float, lng: float, altitude: float = 100.0, speed: float = 15.0, name: str = ""):
        wp = Waypoint(lat, lng, altitude, speed, name)
        self.waypoints.append(wp)
        return wp
    
    def remove_waypoint(self, index: int):
        if 0 <= index < len(self.waypoints):
            del self.waypoints[index]
    
    def update_waypoint(self, index: int, **kwargs):
        if 0 <= index < len(self.waypoints):
            wp = self.waypoints[index]
            if 'lat' in kwargs:
                wp.lat = kwargs['lat']
            if 'lng' in kwargs:
                wp.lng = kwargs['lng']
            if 'altitude' in kwargs:
                wp.altitude = kwargs['altitude']
            if 'speed' in kwargs:
                wp.speed = kwargs['speed']
            if 'name' in kwargs:
                wp.name = kwargs['name']
    
    def add_obstacle(self, name: str, coords: List[Tuple[float, float]], height: float = 50.0):
        obstacle = Obstacle(name, coords, height)
        self.obstacles.append(obstacle)
    
    def remove_obstacle(self, index: int):
        if 0 <= index < len(self.obstacles):
            del self.obstacles[index]
    
    def update_obstacle(self, index: int, **kwargs):
        if 0 <= index < len(self.obstacles):
            obs = self.obstacles[index]
            if 'name' in kwargs:
                obs.name = kwargs['name']
            if 'height' in kwargs:
                obs.height = kwargs['height']
    
    def _line_intersects_obstacle(self, p1: Point, p2: Point) -> Tuple[bool, Optional[Obstacle]]:
        for obstacle in self.obstacles:
            if obstacle.height >= self.uav_altitude:
                if obstacle.distance_to_segment(p1, p2) < self.safety_distance:
                    return True, obstacle
                if obstacle.contains_point(p1) or obstacle.contains_point(p2):
                    return True, obstacle
        return False, None
    
    def _calculate_detour_left(self, p1: Point, p2: Point, obstacle: Obstacle) -> List[Point]:
        centroid = obstacle.get_centroid()
        
        dx = p2.lng - p1.lng
        dy = p2.lat - p1.lat
        perp_dx = -dy
        perp_dy = dx
        
        length = math.sqrt(perp_dx**2 + perp_dy**2)
        if length > 0:
            perp_dx /= length
            perp_dy /= length
        
        offset = self.safety_distance * 3
        detour_lat = centroid.lat + perp_dy * offset
        detour_lng = centroid.lng + perp_dx * offset
        
        return [p1, Point(detour_lat, detour_lng), p2]
    
    def _calculate_detour_right(self, p1: Point, p2: Point, obstacle: Obstacle) -> List[Point]:
        centroid = obstacle.get_centroid()
        
        dx = p2.lng - p1.lng
        dy = p2.lat - p1.lat
        perp_dx = dy
        perp_dy = -dx
        
        length = math.sqrt(perp_dx**2 + perp_dy**2)
        if length > 0:
            perp_dx /= length
            perp_dy /= length
        
        offset = self.safety_distance * 3
        detour_lat = centroid.lat + perp_dy * offset
        detour_lng = centroid.lng + perp_dx * offset
        
        return [p1, Point(detour_lat, detour_lng), p2]
    
    def _calculate_optimal_detour(self, p1: Point, p2: Point, obstacle: Obstacle) -> List[Point]:
        centroid = obstacle.get_centroid()
        
        dx = p2.lng - p1.lng
        dy = p2.lat - p1.lat
        
        px = centroid.lng - p1.lng
        py = centroid.lat - p1.lat
        
        t = (px * dx + py * dy) / (dx**2 + dy**2) if (dx**2 + dy**2) > 0 else 0
        t = max(0, min(1, t))
        
        closest_lat = p1.lat + t * dy
        closest_lng = p1.lng + t * dx
        
        dist_to_line = centroid.distance_to(Point(closest_lat, closest_lng))
        
        perp_dx = -dy
        perp_dy = dx
        length = math.sqrt(perp_dx**2 + perp_dy**2)
        if length > 0:
            perp_dx /= length
            perp_dy /= length
        
        offset = max(dist_to_line / 111 + self.safety_distance, self.safety_distance * 3)
        
        detour_lat1 = closest_lat + perp_dy * offset
        detour_lng1 = closest_lng + perp_dx * offset
        
        detour_lat2 = closest_lat - perp_dy * offset
        detour_lng2 = closest_lng - perp_dx * offset
        
        dist_left = p1.distance_to(Point(detour_lat1, detour_lng1)) + Point(detour_lat1, detour_lng1).distance_to(p2)
        dist_right = p1.distance_to(Point(detour_lat2, detour_lng2)) + Point(detour_lat2, detour_lng2).distance_to(p2)
        
        if dist_left < dist_right:
            return [p1, Point(detour_lat1, detour_lng1), p2]
        else:
            return [p1, Point(detour_lat2, detour_lng2), p2]
    
    def plan_route_with_obstacle_avoidance(self, detour_mode: str = "optimal") -> Tuple[List[Tuple[float, float]], str]:
        if len(self.waypoints) < 2:
            return [(wp.lat, wp.lng) for wp in self.waypoints], "无航点"
        
        route = [(self.waypoints[0].lat, self.waypoints[0].lng)]
        detour_info = ""
        
        for i in range(len(self.waypoints) - 1):
            start = Point(self.waypoints[i].lat, self.waypoints[i].lng)
            end = Point(self.waypoints[i+1].lat, self.waypoints[i+1].lng)
            
            intersects, obstacle = self._line_intersects_obstacle(start, end)
            
            if intersects and obstacle:
                detour_info += f"绕过障碍物: {obstacle.name} "
                
                if detour_mode == "left":
                    detour_points = self._calculate_detour_left(start, end, obstacle)
                    detour_info += "(向左绕飞)"
                elif detour_mode == "right":
                    detour_points = self._calculate_detour_right(start, end, obstacle)
                    detour_info += "(向右绕飞)"
                else:
                    detour_points = self._calculate_optimal_detour(start, end, obstacle)
                    detour_info += "(最优路径)"
                
                for p in detour_points[1:]:
                    route.append((p.lat, p.lng))
            else:
                route.append((end.lat, end.lng))
        
        return route, detour_info
    
    def get_direct_route(self) -> List[Tuple[float, float]]:
        return [(wp.lat, wp.lng) for wp in self.waypoints]
    
    def calculate_total_distance(self, route: Optional[List[Tuple[float, float]]] = None) -> float:
        if route is None:
            route = self.get_direct_route()
        
        total = 0.0
        for i in range(len(route) - 1):
            p1 = Point(route[i][0], route[i][1])
            p2 = Point(route[i+1][0], route[i+1][1])
            total += p1.distance_to(p2)
        return total
    
    def estimate_flight_time(self) -> float:
        total_time = 0.0
        for i in range(len(self.waypoints) - 1):
            p1 = Point(self.waypoints[i].lat, self.waypoints[i].lng)
            p2 = Point(self.waypoints[i+1].lat, self.waypoints[i+1].lng)
            distance = p1.distance_to(p2)
            avg_speed = (self.waypoints[i].speed + self.waypoints[i+1].speed) / 2
            if avg_speed > 0:
                total_time += (distance * 1000) / avg_speed
        return total_time
    
    def save_route(self, filename: str = 'route.json'):
        data = {
            'waypoints': [wp.to_dict() for wp in self.waypoints],
            'obstacles': [{'name': obs.name, 'coords': obs.coords, 'height': obs.height} for obs in self.obstacles],
            'safety_distance': self.safety_distance,
            'uav_altitude': self.uav_altitude
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_route(self, filename: str = 'route.json'):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.waypoints = [Waypoint.from_dict(wp) for wp in data.get('waypoints', [])]
            self.obstacles = [Obstacle(obs['name'], obs['coords'], obs.get('height', 50.0)) for obs in data.get('obstacles', [])]
            self.safety_distance = data.get('safety_distance', 0.0002)
            self.uav_altitude = data.get('uav_altitude', 100.0)
    
    def clear_all(self):
        self.waypoints = []
        self.obstacles = []