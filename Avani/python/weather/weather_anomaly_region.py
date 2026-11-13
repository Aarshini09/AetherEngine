
from math import cos, radians, sqrt
from statistics import fmean


class WeatherAnomalyRegion:
    """
    Represents one spatially connected weather-anomaly region
    at a specific timestamp.

    Coordinates and values describe the anomalous grid nodes
    that belong to this region.

    Area is an approximation based on the supplied grid-node
    coordinates. Exact area requires grid-cell boundaries.
    """

    EARTH_RADIUS_KM = 6371.0088

    def __init__(self, region_id, time, category):
        self.region_id = int(region_id)
        self.time = time
        self.category = category

        self.node_ids = []
        self._nodes = []

        self.min_latitude = None
        self.max_latitude = None
        self.min_longitude = None
        self.max_longitude = None

        self.min_value = None
        self.max_value = None
        self.mean_value = None

        self.min_standardized_anomaly = None
        self.max_standardized_anomaly = None
        self.mean_standardized_anomaly = None

        self.peak_node_id = None
        self.peak_latitude = None
        self.peak_longitude = None

    def add_node(
        self,
        node_id,
        latitude,
        longitude,
        value,
        standardized_anomaly
    ):
        """Add a node and update the region's statistics."""

        node_id = int(node_id)

        if node_id in self.node_ids:
            return

        latitude = float(latitude)
        longitude = float(longitude)
        value = float(value)

        if standardized_anomaly is not None:
            standardized_anomaly = float(
                standardized_anomaly
            )

        node = {
            "node_id": node_id,
            "latitude": latitude,
            "longitude": longitude,
            "value": value,
            "standardized_anomaly": standardized_anomaly
        }

        self.node_ids.append(node_id)
        self._nodes.append(node)

        self._update_bounds(latitude, longitude)
        self._update_value_range(value)
        self._update_peak(node)

        self._recalculate_anomaly_statistics()

    def _update_bounds(self, latitude, longitude):
        if self.min_latitude is None:
            self.min_latitude = latitude
            self.max_latitude = latitude
            self.min_longitude = longitude
            self.max_longitude = longitude
            return

        self.min_latitude = min(
            self.min_latitude, latitude
        )
        self.max_latitude = max(
            self.max_latitude, latitude
        )
        self.min_longitude = min(
            self.min_longitude, longitude
        )
        self.max_longitude = max(
            self.max_longitude, longitude
        )

    def _update_value_range(self, value):
        values = [node["value"] for node in self._nodes]

        self.min_value = min(values)
        self.max_value = max(values)
        self.mean_value = fmean(values)

    def _update_peak(self, node):
        """
        Peak means the largest absolute standardized anomaly,
        not necessarily the largest raw weather value.
        """

        anomaly = node["standardized_anomaly"]

        if anomaly is None:
            return

        current_peak = (
            None if self.peak_node_id is None
            else next(
                item for item in self._nodes
                if item["node_id"] == self.peak_node_id
            )["standardized_anomaly"]
        )

        if (
            current_peak is None
            or abs(anomaly) > abs(current_peak)
        ):
            self.peak_node_id = node["node_id"]
            self.peak_latitude = node["latitude"]
            self.peak_longitude = node["longitude"]

    def _recalculate_anomaly_statistics(self):
        values = [
            node["standardized_anomaly"]
            for node in self._nodes
            if node["standardized_anomaly"] is not None
        ]

        if not values:
            return

        self.min_standardized_anomaly = min(values)
        self.max_standardized_anomaly = max(values)
        self.mean_standardized_anomaly = fmean(values)

    @property
    def node_count(self):
        return len(self.node_ids)

    @property
    def latitude_span(self):
        if self.min_latitude is None:
            return 0.0
        return self.max_latitude - self.min_latitude

    @property
    def longitude_span(self):
        if self.min_longitude is None:
            return 0.0
        return self.max_longitude - self.min_longitude

    @property
    def centroid_latitude(self):
        if not self._nodes:
            return None

        return fmean(
            node["latitude"] for node in self._nodes
        )

    @property
    def centroid_longitude(self):
        """
        Circular mean avoids the ordinary arithmetic-mean
        problem near the antimeridian.
        """

        if not self._nodes:
            return None

        sine = fmean(
            __import__("math").sin(
                radians(node["longitude"])
            )
            for node in self._nodes
        )
        cosine = fmean(
            cos(radians(node["longitude"]))
            for node in self._nodes
        )

        from math import atan2, degrees

        return degrees(atan2(sine, cosine))

    @property
    def approximate_area_km2(self):
        """
        Estimate area from grid-node spacing.

        This approximation assumes a regular latitude/longitude
        grid and is unsuitable as an exact clipped polygon area.
        """

        if len(self._nodes) < 2:
            return 0.0

        latitudes = sorted({
            node["latitude"] for node in self._nodes
        })
        longitudes = sorted({
            node["longitude"] for node in self._nodes
        })

        lat_steps = [
            b - a for a, b in zip(latitudes, latitudes[1:])
            if b > a
        ]
        lon_steps = [
            b - a for a, b in zip(longitudes, longitudes[1:])
            if b > a
        ]

        if not lat_steps or not lon_steps:
            return 0.0

        dlat = radians(fmean(lat_steps))
        dlon = radians(fmean(lon_steps))

        area = 0.0

        for node in self._nodes:
            cell_area = (
                self.EARTH_RADIUS_KM ** 2
                * dlat
                * dlon
                * max(0.0, cos(radians(node["latitude"])))
            )
            area += cell_area

        return area

    @property
    def node_records(self):
        """Return copies of the node records for analysis/serialization."""
        return [dict(node) for node in self._nodes]

    def __repr__(self):
        return (
            f"WeatherAnomalyRegion("
            f"region_id={self.region_id}, "
            f"time={self.time}, "
            f"category={self.category}, "
            f"node_count={self.node_count}, "
            f"centroid=({self.centroid_latitude}, "
            f"{self.centroid_longitude}))"
        )
