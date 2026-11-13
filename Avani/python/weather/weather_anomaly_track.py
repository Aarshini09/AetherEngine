
from datetime import datetime
from math import asin, cos, radians, sin, sqrt


class WeatherAnomalyTrack:
    """
    Represents the temporal evolution of one weather anomaly.

    Stores chronological regions and derives event duration,
    displacement, movement speed, peak intensity, and maximum extent.

    Also records relationships caused by possible splits and merges.
    Relationship metadata does not duplicate region history.
    """

    EARTH_RADIUS_KM = 6371.0088

    def __init__(self, track_id, category):
        self.track_id = int(track_id)
        self.category = category
        self.regions = []

        # Split/merge relationship metadata.
        self.parent_track_ids = set()
        self.child_track_ids = set()
        self.merged_into_track_ids = set()
        self.merged_from_track_ids = set()
        self.lifecycle_events = []

    def add_region(self, region):
        if region.category != self.category:
            raise ValueError(
                "Region category does not match track category."
            )

        if self.regions:
            previous = self.regions[-1]

            if self._time_seconds(region.time) < (
                self._time_seconds(previous.time)
            ):
                raise ValueError(
                    "Track regions must be chronological."
                )

        self.regions.append(region)

    def record_split(self, child_track_id, time):
        """Record that this track produced a child track."""

        child_track_id = int(child_track_id)

        if child_track_id == self.track_id:
            raise ValueError("A track cannot be its own split child.")

        self.child_track_ids.add(child_track_id)

        event = {
            "type": "split",
            "time": time,
            "related_track_id": child_track_id,
        }

        if event not in self.lifecycle_events:
            self.lifecycle_events.append(event)

    def record_parent(self, parent_track_id, time):
        """Record the parent relationship for a newly split track."""

        parent_track_id = int(parent_track_id)

        if parent_track_id == self.track_id:
            raise ValueError("A track cannot be its own parent.")

        self.parent_track_ids.add(parent_track_id)

        event = {
            "type": "split_from",
            "time": time,
            "related_track_id": parent_track_id,
        }

        if event not in self.lifecycle_events:
            self.lifecycle_events.append(event)

    def record_merge(self, other_track_id, time):
        """Record that another track merged into this track."""

        other_track_id = int(other_track_id)

        if other_track_id == self.track_id:
            raise ValueError("A track cannot merge with itself.")

        self.merged_from_track_ids.add(other_track_id)

        event = {
            "type": "merge",
            "time": time,
            "related_track_id": other_track_id,
        }

        if event not in self.lifecycle_events:
            self.lifecycle_events.append(event)

    def record_merged_into(self, survivor_track_id, time):
        """Record that this track merged into a surviving track."""

        survivor_track_id = int(survivor_track_id)

        if survivor_track_id == self.track_id:
            raise ValueError("A track cannot merge into itself.")

        self.merged_into_track_ids.add(survivor_track_id)

        event = {
            "type": "merged_into",
            "time": time,
            "related_track_id": survivor_track_id,
        }

        if event not in self.lifecycle_events:
            self.lifecycle_events.append(event)

    @staticmethod
    def _time_seconds(value):
        if isinstance(value, datetime):
            return value.timestamp()

        try:
            import numpy as np

            timestamp = np.datetime64(value, "ns")

            if np.isnat(timestamp):
                raise ValueError("Timestamp cannot be NaT.")

            return float(timestamp.astype("int64")) / 1_000_000_000
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                f"Unsupported track timestamp: {value!r}"
            ) from error

    @property
    def region_count(self):
        return len(self.regions)

    @property
    def start_time(self):
        return self.regions[0].time if self.regions else None

    @property
    def end_time(self):
        return self.regions[-1].time if self.regions else None

    @property
    def duration_count(self):
        return self.region_count

    @property
    def duration_seconds(self):
        if len(self.regions) < 2:
            return 0.0

        return (
            self._time_seconds(self.end_time)
            - self._time_seconds(self.start_time)
        )

    @property
    def duration_hours(self):
        return self.duration_seconds / 3600.0

    @staticmethod
    def _haversine_km(lat1, lon1, lat2, lon2):
        lat1 = radians(lat1)
        lat2 = radians(lat2)
        dlat = lat2 - lat1

        dlon = radians(lon2 - lon1)
        dlon = (dlon + 3.141592653589793) % (
            2 * 3.141592653589793
        ) - 3.141592653589793

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        )

        return 2 * WeatherAnomalyTrack.EARTH_RADIUS_KM * asin(
            min(1.0, sqrt(max(0.0, a)))
        )

    @property
    def trajectory(self):
        """Chronological centroid positions, one per region."""

        return [
            {
                "time": region.time,
                "latitude": region.centroid_latitude,
                "longitude": region.centroid_longitude,
            }
            for region in self.regions
        ]

    @property
    def displacement_km(self):
        if len(self.regions) < 2:
            return 0.0

        first = self.regions[0]
        last = self.regions[-1]

        return self._haversine_km(
            first.centroid_latitude,
            first.centroid_longitude,
            last.centroid_latitude,
            last.centroid_longitude,
        )

    @property
    def path_length_km(self):
        total = 0.0

        for first, second in zip(
            self.regions, self.regions[1:]
        ):
            total += self._haversine_km(
                first.centroid_latitude,
                first.centroid_longitude,
                second.centroid_latitude,
                second.centroid_longitude,
            )

        return total

    @property
    def mean_speed_kmh(self):
        if self.duration_hours <= 0:
            return None

        return self.path_length_km / self.duration_hours

    @property
    def peak_standardized_anomaly(self):
        values = [
            abs(region.max_standardized_anomaly)
            for region in self.regions
            if region.max_standardized_anomaly is not None
        ]

        return max(values) if values else None

    @property
    def maximum_area_km2(self):
        return max(
            (
                region.approximate_area_km2
                for region in self.regions
            ),
            default=0.0,
        )

    def get_region(self, index):
        return self.regions[index]

    def get_last_region(self):
        return self.regions[-1] if self.regions else None

    def __repr__(self):
        return (
            f"WeatherAnomalyTrack("
            f"track_id={self.track_id}, "
            f"category={self.category}, "
            f"region_count={self.region_count}, "
            f"duration_hours={self.duration_hours:.2f}, "
            f"path_length_km={self.path_length_km:.2f}, "
            f"parents={sorted(self.parent_track_ids)}, "
            f"children={sorted(self.child_track_ids)})"
        )
