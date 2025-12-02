"""
Watershed analysis and delineation
"""

import logging
from typing import List, Tuple, Dict, Optional
import numpy as np
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from scipy.spatial import Voronoi
from app.spatial.simple_processor import SimpleSpatialProcessor

logger = logging.getLogger(__name__)


class WatershedAnalyzer:
    """
    Watershed analysis and delineation tools
    Simplified implementation without full DEM processing
    """

    def __init__(self):
        self.spatial_processor = SimpleSpatialProcessor()
        logger.info("Watershed analyzer initialized")

    def create_drainage_basins(
        self,
        gauge_points: List[Tuple[float, float]],
        bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> List[Polygon]:
        """
        Create approximate drainage basins using Voronoi polygons

        Args:
            gauge_points: List of (longitude, latitude) tuples for gauge locations
            bbox: Optional bounding box (minx, miny, maxx, maxy)

        Returns:
            List of drainage basin polygons
        """
        if len(gauge_points) < 3:
            logger.warning("Need at least 3 gauge points for Voronoi analysis")
            return []

        try:
            # Convert to numpy array
            points = np.array(gauge_points)

            # Create Voronoi diagram
            vor = Voronoi(points)

            basins = []

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
                        from shapely.geometry import box
                        bbox_poly = box(*bbox)
                        poly = poly.intersection(bbox_poly)

                    if not poly.is_empty and poly.is_valid:
                        basins.append(poly)

            logger.info(f"Created {len(basins)} drainage basins")
            return basins

        except Exception as e:
            logger.error(f"Error creating drainage basins: {e}")
            return []

    def calculate_basin_properties(
        self,
        basin_polygon: Polygon,
        gauge_location: Tuple[float, float],
        elevation_data: Optional[List[Tuple[float, float, float]]] = None
    ) -> Dict:
        """
        Calculate watershed/basin properties

        Args:
            basin_polygon: Drainage basin polygon
            gauge_location: (longitude, latitude) of outlet gauge
            elevation_data: Optional list of (lon, lat, elevation) points

        Returns:
            Dictionary with basin properties
        """
        try:
            # Calculate area
            area_sq_meters = self.spatial_processor.calculate_area_square_meters(basin_polygon)
            area_sq_miles = area_sq_meters / 2589988.11  # Convert to square miles

            # Calculate perimeter
            perimeter_meters = basin_polygon.length * 111320  # Approximate conversion

            # Calculate shape metrics
            circularity = (4 * np.pi * area_sq_meters) / (perimeter_meters ** 2)

            # Calculate centroid
            centroid = basin_polygon.centroid

            properties = {
                'area_sq_miles': round(area_sq_miles, 2),
                'area_sq_meters': round(area_sq_meters, 2),
                'perimeter_meters': round(perimeter_meters, 2),
                'circularity': round(circularity, 3),
                'centroid': {
                    'longitude': centroid.x,
                    'latitude': centroid.y
                },
                'outlet_location': {
                    'longitude': gauge_location[0],
                    'latitude': gauge_location[1]
                }
            }

            # Add elevation-based properties if available
            if elevation_data:
                elevations = [e[2] for e in elevation_data 
                            if basin_polygon.contains(Point(e[0], e[1]))]

                if elevations:
                    properties['elevation_min_ft'] = round(min(elevations), 1)
                    properties['elevation_max_ft'] = round(max(elevations), 1)
                    properties['elevation_mean_ft'] = round(np.mean(elevations), 1)
                    properties['elevation_range_ft'] = round(max(elevations) - min(elevations), 1)

                    # Calculate average slope (simplified)
                    if len(elevations) > 1:
                        slope = properties['elevation_range_ft'] / (perimeter_meters * 3.28084)
                        properties['average_slope_percent'] = round(slope * 100, 2)

            return properties

        except Exception as e:
            logger.error(f"Error calculating basin properties: {e}")
            return {}

    def identify_upstream_gauges(
        self,
        outlet_gauge: Tuple[float, float],
        all_gauges: List[Dict],
        search_radius_km: float = 50.0
    ) -> List[Dict]:
        """
        Identify gauges upstream of a given outlet
        Simplified method based on distance and general flow direction

        Args:
            outlet_gauge: (longitude, latitude) of outlet gauge
            all_gauges: List of gauge dictionaries with coordinates
            search_radius_km: Search radius in kilometers

        Returns:
            List of upstream gauge dictionaries
        """
        upstream_gauges = []

        for gauge in all_gauges:
            gauge_loc = (gauge.get('longitude'), gauge.get('latitude'))

            # Calculate distance
            distance = self.spatial_processor.calculate_distance_meters(
                outlet_gauge,
                gauge_loc
            ) / 1000  # Convert to km

            if distance > search_radius_km or distance < 0.1:  # Exclude self
                continue

            # Simple heuristic: gauges at higher elevation are likely upstream
            # In reality, would need actual flow direction analysis
            if gauge.get('elevation_ft', 0) > 0:  # Has elevation data
                upstream_gauges.append({
                    **gauge,
                    'distance_km': round(distance, 2)
                })

        # Sort by distance
        upstream_gauges.sort(key=lambda x: x['distance_km'])

        return upstream_gauges

    def calculate_time_of_concentration(
        self,
        basin_properties: Dict,
        method: str = 'kirpich'
    ) -> float:
        """
        Calculate time of concentration for a watershed

        Args:
            basin_properties: Basin properties from calculate_basin_properties
            method: Calculation method ('kirpich', 'scs', 'bransby_williams')

        Returns:
            Time of concentration in hours
        """
        try:
            area_sq_miles = basin_properties.get('area_sq_miles', 0)
            slope_percent = basin_properties.get('average_slope_percent', 1)

            if method == 'kirpich':
                # Kirpich formula (for small watersheds)
                # Tc = 0.0078 * L^0.77 * S^-0.385
                # Simplified using area as proxy for length
                length_miles = np.sqrt(area_sq_miles)
                slope_fraction = slope_percent / 100

                if slope_fraction > 0:
                    tc_minutes = 0.0078 * (length_miles * 5280) ** 0.77 * slope_fraction ** -0.385
                    return round(tc_minutes / 60, 2)  # Convert to hours

            elif method == 'scs':
                # SCS method
                # Simplified calculation
                length_miles = np.sqrt(area_sq_miles)
                tc_hours = 0.057 * (length_miles ** 0.8) / (slope_percent ** 0.5)
                return round(tc_hours, 2)

            # Default fallback
            return round(area_sq_miles * 0.5, 2)  # Very rough estimate

        except Exception as e:
            logger.error(f"Error calculating time of concentration: {e}")
            return 1.0  # Default 1 hour

    def estimate_runoff_curve_number(
        self,
        land_use_type: str = 'urban_medium_density'
    ) -> int:
        """
        Estimate SCS Curve Number based on land use

        Args:
            land_use_type: Type of land use

        Returns:
            Curve number (0-100)
        """
        # Simplified curve numbers (assuming average conditions)
        curve_numbers = {
            'urban_high_density': 85,
            'urban_medium_density': 75,
            'urban_low_density': 65,
            'commercial': 88,
            'industrial': 82,
            'residential': 70,
            'forest': 55,
            'agricultural': 72,
            'pasture': 68,
            'water': 100,
            'wetland': 90,
        }

        return curve_numbers.get(land_use_type, 70)  # Default to residential

    def calculate_peak_discharge(
        self,
        basin_properties: Dict,
        rainfall_inches: float,
        curve_number: int = 70
    ) -> float:
        """
        Calculate peak discharge using SCS method

        Args:
            basin_properties: Basin properties
            rainfall_inches: Rainfall amount in inches
            curve_number: SCS curve number

        Returns:
            Peak discharge in cfs
        """
        try:
            area_sq_miles = basin_properties.get('area_sq_miles', 1)
            tc_hours = self.calculate_time_of_concentration(basin_properties)

            # Calculate runoff using SCS method
            # S = (1000/CN) - 10
            S = (1000 / curve_number) - 10

            # Initial abstraction
            Ia = 0.2 * S

            # Runoff depth
            if rainfall_inches > Ia:
                runoff_inches = ((rainfall_inches - Ia) ** 2) / (rainfall_inches - Ia + S)
            else:
                runoff_inches = 0

            # Peak discharge using rational method approximation
            # Q = C * I * A (simplified)
            # Where C depends on curve number, I is intensity, A is area
            intensity = rainfall_inches / tc_hours  # inches/hour

            # Simplified peak discharge
            peak_discharge = 0.5 * (curve_number / 100) * intensity * area_sq_miles * 640  # Convert to cfs

            return round(peak_discharge, 2)

        except Exception as e:
            logger.error(f"Error calculating peak discharge: {e}")
            return 0.0

    def analyze_flood_path(
        self,
        start_point: Tuple[float, float],
        gauge_points: List[Tuple[float, float]],
        max_distance_km: float = 20.0
    ) -> List[Tuple[float, float]]:
        """
        Analyze likely flood propagation path
        Simplified method based on proximity to gauges

        Args:
            start_point: Starting point (longitude, latitude)
            gauge_points: List of gauge locations
            max_distance_km: Maximum distance to consider

        Returns:
            List of points along the flood path
        """
        path = [start_point]
        current_point = start_point
        visited = set()

        while len(path) < 10:  # Limit path length
            nearest = None
            nearest_dist = float('inf')

            for gauge_point in gauge_points:
                if tuple(gauge_point) in visited:
                    continue

                dist_km = self.spatial_processor.calculate_distance_meters(
                    current_point, gauge_point
                ) / 1000

                if dist_km < nearest_dist and dist_km < max_distance_km:
                    nearest = gauge_point
                    nearest_dist = dist_km

            if nearest is None:
                break

            path.append(tuple(nearest))
            visited.add(tuple(nearest))
            current_point = nearest

        return path