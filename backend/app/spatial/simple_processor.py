import logging
from typing import List, Tuple, Optional, Dict
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon, box, LineString
from shapely.ops import unary_union, transform
from scipy.spatial import Voronoi, distance
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import pyproj
from functools import partial

logger = logging.getLogger(__name__)

class SimpleSpatialProcessor:
    """
    Spatial processor using only pure Python libraries
    No GDAL, QGIS, or GeoPandas dependencies
    """
    
    def __init__(self):
        # WGS84 to Web Mercator transformer for distance calculations
        self.wgs84 = pyproj.CRS('EPSG:4326')
        self.web_mercator = pyproj.CRS('EPSG:3857')
        self.to_meters = pyproj.Transformer.from_crs(
            self.wgs84, self.web_mercator, always_xy=True
        )
        self.to_degrees = pyproj.Transformer.from_crs(
            self.web_mercator, self.wgs84, always_xy=True
        )
        logger.info("Pure Python spatial processor initialized")
    
    def create_buffer_zone(
        self, 
        points: List[Tuple[float, float]], 
        buffer_distance: float = 1000
    ) -> List[Polygon]:
        """
        Create buffer zones around gauge points
        
        Args:
            points: List of (longitude, latitude) tuples
            buffer_distance: Buffer distance in meters
        
        Returns:
            List of buffer polygons
        """
        buffers = []
        
        for lon, lat in points:
            # Create point
            point = Point(lon, lat)
            
            # Transform to projected CRS for accurate buffering
            project = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'),
                pyproj.Proj(init='epsg:3857')
            )
            
            point_proj = transform(project, point)
            
            # Create buffer
            buffer_proj = point_proj.buffer(buffer_distance)
            
            # Transform back to geographic CRS
            project_back = partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:3857'),
                pyproj.Proj(init='epsg:4326')
            )
            
            buffer = transform(project_back, buffer_proj)
            buffers.append(buffer)
        
        return buffers
    
    def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points in meters
        
        Args:
            point1: (longitude, latitude)
            point2: (longitude, latitude)
        
        Returns:
            Distance in meters
        """
        x1, y1 = self.to_meters.transform(point1[0], point1[1])
        x2, y2 = self.to_meters.transform(point2[0], point2[1])
        
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def create_voronoi_polygons(
        self,
        points: List[Tuple[float, float]],
        bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> List[Polygon]:
        """
        Create Voronoi (Thiessen) polygons from points
        
        Args:
            points: List of (longitude, latitude) tuples
            bbox: Optional bounding box (minx, miny, maxx, maxy)
        
        Returns:
            List of Voronoi polygons
        """
        if len(points) < 3:
            return []
        
        # Convert points to numpy array
        points_array = np.array(points)
        
        # Create Voronoi diagram
        vor = Voronoi(points_array)
        
        polygons = []
        
        # Create polygons from Voronoi regions
        for region_idx in vor.point_region:
            region = vor.regions[region_idx]
            
            if not region or -1 in region:
                continue
            
            vertices = [vor.vertices[i] for i in region]
            
            if len(vertices) >= 3:
                poly = Polygon(vertices)
                
                # Clip to bounding box if provided
                if bbox:
                    bbox_poly = box(*bbox)
                    poly = poly.intersection(bbox_poly)
                
                if not poly.is_empty:
                    polygons.append(poly)
        
        return polygons
    
    def interpolate_risk_surface(
        self,
        points: List[Tuple[float, float]],
        values: List[float],
        grid_resolution: int = 100,
        method: str = 'cubic'
    ) -> Dict[str, np.ndarray]:
        """
        Interpolate risk values across a surface
        
        Args:
            points: List of (longitude, latitude) tuples
            values: Risk values at each point
            grid_resolution: Number of grid points per dimension
            method: Interpolation method ('linear', 'cubic', 'nearest')
        
        Returns:
            Dictionary with longitude, latitude, and risk grids
        """
        if len(points) < 3:
            return {}
        
        points_array = np.array(points)
        values_array = np.array(values)
        
        # Create grid
        lon_min, lat_min = points_array.min(axis=0)
        lon_max, lat_max = points_array.max(axis=0)
        
        # Add padding
        padding = 0.1
        lon_min -= padding
        lat_min -= padding
        lon_max += padding
        lat_max += padding
        
        grid_lon = np.linspace(lon_min, lon_max, grid_resolution)
        grid_lat = np.linspace(lat_min, lat_max, grid_resolution)
        
        grid_lon_mesh, grid_lat_mesh = np.meshgrid(grid_lon, grid_lat)
        
        # Interpolate
        grid_risk = griddata(
            points_array,
            values_array,
            (grid_lon_mesh, grid_lat_mesh),
            method=method,
            fill_value=0
        )
        
        # Apply smoothing
        grid_risk = gaussian_filter(grid_risk, sigma=1.0)
        
        # Clip to valid range
        grid_risk = np.clip(grid_risk, 0, 100)
        
        return {
            'longitude': grid_lon,
            'latitude': grid_lat,
            'risk_values': grid_risk
        }
    
    def calculate_flow_direction_simple(
        self,
        points: List[Tuple[float, float, float]],  # lon, lat, elevation
        cell_size: float = 30.0
    ) -> Dict[str, np.ndarray]:
        """
        Simple flow direction calculation from point elevations
        
        Args:
            points: List of (longitude, latitude, elevation) tuples
            cell_size: Grid cell size in meters
        
        Returns:
            Dictionary with flow direction grid
        """
        if len(points) < 4:
            return {}
        
        # Extract coordinates and elevations
        coords = np.array([(p[0], p[1]) for p in points])
        elevations = np.array([p[2] for p in points])
        
        # Create regular grid
        lon_min, lat_min = coords.min(axis=0)
        lon_max, lat_max = coords.max(axis=0)
        
        # Estimate number of cells based on cell size
        x_min, y_min = self.to_meters.transform(lon_min, lat_min)
        x_max, y_max = self.to_meters.transform(lon_max, lat_max)
        
        n_cols = int((x_max - x_min) / cell_size) + 1
        n_rows = int((y_max - y_min) / cell_size) + 1
        
        grid_lon = np.linspace(lon_min, lon_max, n_cols)
        grid_lat = np.linspace(lat_min, lat_max, n_rows)
        
        grid_lon_mesh, grid_lat_mesh = np.meshgrid(grid_lon, grid_lat)
        
        # Interpolate elevations
        grid_elevation = griddata(
            coords,
            elevations,
            (grid_lon_mesh, grid_lat_mesh),
            method='cubic',
            fill_value=np.nan
        )
        
        # Calculate slope components
        dy, dx = np.gradient(grid_elevation)
        
        # Calculate flow direction (angle in radians)
        flow_direction = np.arctan2(-dy, -dx)
        
        return {
            'longitude': grid_lon,
            'latitude': grid_lat,
            'elevation': grid_elevation,
            'flow_direction': flow_direction,
            'slope': np.sqrt(dx**2 + dy**2)
        }
    
    def identify_low_areas(
        self,
        points: List[Tuple[float, float, float]],  # lon, lat, elevation
        threshold_percentile: float = 25.0
    ) -> List[Tuple[float, float]]:
        """
        Identify low-lying areas based on elevation percentile
        
        Args:
            points: List of (longitude, latitude, elevation) tuples
            threshold_percentile: Elevation percentile threshold (0-100)
        
        Returns:
            List of (longitude, latitude) tuples in low areas
        """
        if not points:
            return []
        
        elevations = np.array([p[2] for p in points])
        threshold = np.percentile(elevations, threshold_percentile)
        
        low_points = [
            (p[0], p[1]) 
            for p in points 
            if p[2] <= threshold
        ]
        
        return low_points
    
    def calculate_proximity_risk(
        self,
        query_points: List[Tuple[float, float]],
        water_bodies: List[Tuple[float, float]],
        max_distance: float = 2000.0
    ) -> List[float]:
        """
        Calculate proximity-based risk scores
        
        Args:
            query_points: List of (longitude, latitude) tuples to assess
            water_bodies: List of (longitude, latitude) tuples of water bodies
            max_distance: Maximum distance for risk calculation (meters)
        
        Returns:
            List of risk scores (0-100) for each query point
        """
        if not query_points or not water_bodies:
            return [0.0] * len(query_points)
        
        risk_scores = []
        
        for qpoint in query_points:
            # Calculate distance to nearest water body
            min_distance = float('inf')
            
            for wpoint in water_bodies:
                dist = self.calculate_distance(qpoint, wpoint)
                min_distance = min(min_distance, dist)
            
            # Convert distance to risk score (inverse relationship)
            if min_distance >= max_distance:
                risk = 0.0
            else:
                risk = 100.0 * (1.0 - (min_distance / max_distance))
            
            risk_scores.append(risk)
        
        return risk_scores
    
    def calculate_slope_from_points(
        self,
        points: List[Tuple[float, float, float]],  # lon, lat, elevation
        query_point: Tuple[float, float],
        neighborhood_radius: float = 500.0
    ) -> float:
        """
        Calculate average slope near a query point
        
        Args:
            points: List of (longitude, latitude, elevation) tuples
            query_point: (longitude, latitude) to query
            neighborhood_radius: Radius in meters to consider
        
        Returns:
            Average slope in degrees
        """
        if len(points) < 3:
            return 0.0
        
        # Find points within radius
        nearby_points = []
        
        for p in points:
            dist = self.calculate_distance(query_point, (p[0], p[1]))
            if dist <= neighborhood_radius:
                nearby_points.append(p)
        
        if len(nearby_points) < 3:
            return 0.0
        
        # Calculate slopes between point pairs
        slopes = []
        
        for i, p1 in enumerate(nearby_points):
            for p2 in nearby_points[i+1:]:
                horizontal_dist = self.calculate_distance(
                    (p1[0], p1[1]),
                    (p2[0], p2[1])
                )
                
                if horizontal_dist > 0:
                    vertical_dist = abs(p2[2] - p1[2])
                    slope_rad = np.arctan(vertical_dist / horizontal_dist)
                    slope_deg = np.degrees(slope_rad)
                    slopes.append(slope_deg)
        
        return np.mean(slopes) if slopes else 0.0
    
    def create_contour_lines(
        self,
        points: List[Tuple[float, float, float]],  # lon, lat, elevation
        contour_intervals: List[float],
        grid_resolution: int = 100
    ) -> Dict[float, List[LineString]]:
        """
        Create contour lines from elevation points
        
        Args:
            points: List of (longitude, latitude, elevation) tuples
            contour_intervals: List of elevation values for contours
            grid_resolution: Grid resolution for interpolation
        
        Returns:
            Dictionary mapping elevation to list of contour LineStrings
        """
        if len(points) < 4:
            return {}
        
        # Interpolate elevation grid
        coords = np.array([(p[0], p[1]) for p in points])
        elevations = np.array([p[2] for p in points])
        
        lon_min, lat_min = coords.min(axis=0)
        lon_max, lat_max = coords.max(axis=0)
        
        grid_lon = np.linspace(lon_min, lon_max, grid_resolution)
        grid_lat = np.linspace(lat_min, lat_max, grid_resolution)
        
        grid_lon_mesh, grid_lat_mesh = np.meshgrid(grid_lon, grid_lat)
        
        grid_elevation = griddata(
            coords,
            elevations,
            (grid_lon_mesh, grid_lat_mesh),
            method='cubic'
        )
        
        # Use matplotlib for contouring (optional, can be pure numpy)
        try:
            import matplotlib.pyplot as plt
            from matplotlib.path import Path
            
            contours_dict = {}
            
            fig, ax = plt.subplots()
            cs = ax.contour(grid_lon, grid_lat, grid_elevation, levels=contour_intervals)
            
            for level, collection in zip(cs.levels, cs.collections):
                paths = collection.get_paths()
                lines = []
                
                for path in paths:
                    vertices = path.vertices
                    if len(vertices) > 1:
                        lines.append(LineString(vertices))
                
                contours_dict[level] = lines
            
            plt.close(fig)
            
            return contours_dict
            
        except ImportError:
            logger.warning("Matplotlib not available for contour generation")
            return {}
    
    def point_in_polygon(
        self,
        point: Tuple[float, float],
        polygon: Polygon
    ) -> bool:
        """Check if point is inside polygon"""
        return Point(point).within(polygon)
    
    def get_bounding_box(
        self,
        points: List[Tuple[float, float]]
    ) -> Tuple[float, float, float, float]:
        """
        Get bounding box for points
        
        Returns:
            (min_lon, min_lat, max_lon, max_lat)
        """
        if not points:
            return (0, 0, 0, 0)
        
        points_array = np.array(points)
        min_coords = points_array.min(axis=0)
        max_coords = points_array.max(axis=0)
        
        return (min_coords[0], min_coords[1], max_coords[0], max_coords[1])