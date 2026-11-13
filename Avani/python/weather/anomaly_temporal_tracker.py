
from datetime import datetime
from math import asin, cos, radians, sin, sqrt

import numpy as np

from weather.weather_anomaly_track import WeatherAnomalyTrack


class AnomalyTemporalTracker:
    """
    Associate weather anomaly regions across timestamps.

    Features:
        - Great-circle centroid distance.
        - Category-aware global one-to-one assignment.
        - Region-shape and intensity matching evidence.
        - Missing-observation bridging.
        - Elapsed-time-aware distance thresholds.
        - Split/merge relationship metadata.
        - Preservation of expired and merged tracks.

    Split/merge relationships are candidate relationships inferred
    from spatial and temporal compatibility. They are not proof of
    physical meteorological splitting or merging.
    """

    EARTH_RADIUS_KM = 6371.0088

    def __init__(
        self,
        maximum_distance_km=300.0,
        expected_interval_hours=6.0,
        max_missed_observations=1,
        maximum_shape_distance_km=150.0,
        intensity_weight_km=50.0,
    ):
        self.maximum_distance_km = float(maximum_distance_km)
        self.expected_interval_hours = float(expected_interval_hours)
        self.maximum_shape_distance_km = float(
            maximum_shape_distance_km
        )
        self.intensity_weight_km = float(intensity_weight_km)

        for name, value in (
            ("maximum_distance_km", self.maximum_distance_km),
            ("expected_interval_hours", self.expected_interval_hours),
            (
                "maximum_shape_distance_km",
                self.maximum_shape_distance_km,
            ),
            ("intensity_weight_km", self.intensity_weight_km),
        ):
            if not np.isfinite(value) or value <= 0:
                raise ValueError(
                    f"{name} must be finite and positive."
                )

        if (
            isinstance(max_missed_observations, bool)
            or not isinstance(
                max_missed_observations, (int, np.integer)
            )
            or max_missed_observations < 0
        ):
            raise ValueError(
                "max_missed_observations must be a "
                "non-negative integer."
            )

        self.max_missed_observations = int(
            max_missed_observations
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build_tracks(self, region_fields):
        """
        Build tracks from timestamped region fields.

        Each field:
            {"time": timestamp, "regions": [region, ...]}

        Returns all tracks, including expired and merged tracks.
        """

        if region_fields is None:
            raise ValueError("region_fields cannot be None.")

        normalized_fields = []

        for index, field in enumerate(list(region_fields)):
            if not isinstance(field, dict):
                raise TypeError(
                    f"Region field {index} must be a dictionary."
                )

            if "time" not in field or "regions" not in field:
                raise ValueError(
                    f"Region field {index} requires 'time' and 'regions'."
                )

            if field["time"] is None:
                raise ValueError(
                    f"Region field {index} has no timestamp."
                )

            if field["regions"] is None:
                raise ValueError(
                    f"Region field {index} has regions=None; "
                    "use an empty list for no observed regions."
                )

            normalized_fields.append({
                "time": field["time"],
                "regions": list(field["regions"]),
            })

        if not normalized_fields:
            return []

        normalized_fields.sort(
            key=lambda field: self._time_seconds(field["time"])
        )

        timestamps = [
            self._time_seconds(field["time"])
            for field in normalized_fields
        ]

        for previous, current in zip(
            timestamps, timestamps[1:]
        ):
            if current <= previous:
                raise ValueError(
                    "Region field timestamps must be unique and increasing."
                )

        all_tracks = []
        active_tracks = []
        next_track_id = 0

        for field in normalized_fields:
            current_time = field["time"]
            regions = field["regions"]

            if not regions:
                active_tracks = self._advance_unmatched_tracks(
                    active_tracks
                )
                continue

            # First non-empty observation: create initial tracks.
            if not active_tracks:
                for region in regions:
                    track = self._create_track(
                        next_track_id, region
                    )
                    next_track_id += 1

                    active_tracks.append({
                        "track": track,
                        "missed": 0,
                    })
                    all_tracks.append(track)

                continue

            tracks = [
                entry["track"] for entry in active_tracks
            ]

            # Candidate relationships are calculated independently
            # of the final one-to-one Hungarian assignment.
            compatible = self._compatible_region_pairs(
                tracks, regions, current_time
            )

            matches = self._match_regions(
                tracks, regions, current_time=current_time
            )

            matched_track_indices = set(matches)
            matched_region_indices = set(matches.values())

            # A track is a merge candidate when it is compatible
            # with a current region assigned to another track.
            # Only unmatched old tracks can be consumed by a merge.
            merged_track_to_survivor = {}

            for survivor_index, region_index in matches.items():
                for other_index in range(len(tracks)):
                    if other_index == survivor_index:
                        continue

                    if other_index in matched_track_indices:
                        continue

                    if region_index not in compatible[other_index]:
                        continue

                    survivor = tracks[survivor_index]
                    other = tracks[other_index]

                    survivor.record_merge(
                        other.track_id, current_time
                    )
                    other.record_merged_into(
                        survivor.track_id, current_time
                    )

                    merged_track_to_survivor[other_index] = (
                        survivor_index
                    )

            next_active_tracks = []

            # Continue tracks selected by global assignment.
            for track_index, region_index in matches.items():
                track = tracks[track_index]
                track.add_region(regions[region_index])

                next_active_tracks.append({
                    "track": track,
                    "missed": 0,
                })

            # Retain unmatched tracks unless they merged or expired.
            for track_index, entry in enumerate(active_tracks):
                if track_index in matched_track_indices:
                    continue

                if track_index in merged_track_to_survivor:
                    continue

                missed = entry["missed"] + 1

                if missed <= self.max_missed_observations:
                    next_active_tracks.append({
                        "track": entry["track"],
                        "missed": missed,
                    })

            # Create tracks for unmatched current regions.
            new_tracks_by_region = {}

            for region_index, region in enumerate(regions):
                if region_index in matched_region_indices:
                    continue

                track = self._create_track(
                    next_track_id, region
                )
                next_track_id += 1

                new_tracks_by_region[region_index] = track
                next_active_tracks.append({
                    "track": track,
                    "missed": 0,
                })
                all_tracks.append(track)

            # Split detection:
            # A continuing parent must have been matched to one
            # current region and be compatible with another, newly
            # created region at the same timestamp.
            for parent_index, parent_track in enumerate(tracks):
                if parent_index not in matches:
                    continue

                parent_region_index = matches[parent_index]

                for child_region_index, child_track in (
                    new_tracks_by_region.items()
                ):
                    if child_region_index == parent_region_index:
                        continue

                    if (
                        child_region_index
                        not in compatible[parent_index]
                    ):
                        continue

                    parent_track.record_split(
                        child_track.track_id, current_time
                    )
                    child_track.record_parent(
                        parent_track.track_id, current_time
                    )

            active_tracks = sorted(
                next_active_tracks,
                key=lambda entry: entry["track"].track_id,
            )

        return all_tracks

    def region_distance_km(self, first_region, second_region):
        """Great-circle distance between region centroids."""

        lat1, lon1 = self._region_centroid(first_region)
        lat2, lon2 = self._region_centroid(second_region)

        lat1 = radians(lat1)
        lat2 = radians(lat2)

        delta_lat = lat2 - lat1
        delta_lon = radians(
            self._wrapped_longitude_difference(lon1, lon2)
        )

        haversine = (
            sin(delta_lat / 2.0) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2.0) ** 2
        )

        haversine = min(1.0, max(0.0, haversine))

        return (
            2.0 * self.EARTH_RADIUS_KM
            * asin(sqrt(haversine))
        )

    # ---------------------------------------------------------
    # Candidate relationship detection
    # ---------------------------------------------------------

    def _compatible_region_pairs(
        self, tracks, regions, current_time
    ):
        """
        Return candidate current-region indices for each track.

        Uses the same category, time, distance, and optional shape
        gates as ordinary matching. This does not override the
        one-to-one Hungarian assignment.
        """

        compatible = {
            index: set() for index in range(len(tracks))
        }

        current_seconds = self._time_seconds(current_time)
        maximum_intervals = self.max_missed_observations + 1

        for track_index, track in enumerate(tracks):
            previous = track.get_last_region()

            if previous is None:
                continue

            elapsed_hours = (
                current_seconds - self._time_seconds(previous.time)
            ) / 3600.0

            if not (
                0 < elapsed_hours
                <= self.expected_interval_hours * maximum_intervals
            ):
                continue

            distance_limit = self._maximum_match_distance(
                elapsed_hours
            )

            for region_index, region in enumerate(regions):
                if region.category != track.category:
                    continue

                if (
                    self.region_distance_km(previous, region)
                    > distance_limit
                ):
                    continue

                shape_distance = self._region_shape_distance_km(
                    previous, region
                )

                if (
                    shape_distance is not None
                    and shape_distance
                    > self.maximum_shape_distance_km
                ):
                    continue

                compatible[track_index].add(region_index)

        return compatible

    # ---------------------------------------------------------
    # Track lifecycle
    # ---------------------------------------------------------

    def _advance_unmatched_tracks(self, active_tracks):
        next_active_tracks = []

        for entry in active_tracks:
            missed = entry["missed"] + 1

            if missed <= self.max_missed_observations:
                next_active_tracks.append({
                    "track": entry["track"],
                    "missed": missed,
                })

        return sorted(
            next_active_tracks,
            key=lambda entry: entry["track"].track_id,
        )

    def _maximum_match_distance(self, elapsed_hours):
        if (
            not np.isfinite(elapsed_hours)
            or elapsed_hours <= 0
        ):
            return 0.0

        elapsed_intervals = (
            elapsed_hours / self.expected_interval_hours
        )

        maximum_intervals = self.max_missed_observations + 1

        return self.maximum_distance_km * min(
            elapsed_intervals, maximum_intervals
        )

    # ---------------------------------------------------------
    # Matching
    # ---------------------------------------------------------

    def _match_regions(self, tracks, regions, current_time=None):
        """Globally assign compatible tracks to current regions."""

        track_count = len(tracks)
        region_count = len(regions)

        if track_count == 0 or region_count == 0:
            return {}

        current_seconds = self._time_seconds(
            current_time if current_time is not None else regions[0].time
        )

        maximum_intervals = self.max_missed_observations + 1

        maximum_valid_cost = (
            self.maximum_distance_km * maximum_intervals
            + self.maximum_shape_distance_km
            + self.intensity_weight_km
        )

        unmatched_cost = (
            (min(track_count, region_count) + 1)
            * (maximum_valid_cost + 1.0)
        )

        invalid_cost = unmatched_cost * (
            track_count + region_count + 2
        )

        costs = []

        for track_index, track in enumerate(tracks):
            previous = track.get_last_region()
            previous_seconds = self._time_seconds(previous.time)

            elapsed_hours = (
                current_seconds - previous_seconds
            ) / 3600.0

            valid_elapsed = (
                0 < elapsed_hours
                <= self.expected_interval_hours * maximum_intervals
            )

            distance_limit = self._maximum_match_distance(
                elapsed_hours
            )

            row = []

            for region_index, region in enumerate(regions):
                if (
                    not valid_elapsed
                    or region.category != track.category
                ):
                    row.append(invalid_cost)
                    continue

                distance = self.region_distance_km(
                    previous, region
                )

                if distance > distance_limit:
                    row.append(invalid_cost)
                    continue

                shape_distance = self._region_shape_distance_km(
                    previous, region
                )

                if (
                    shape_distance is not None
                    and shape_distance
                    > self.maximum_shape_distance_km
                ):
                    row.append(invalid_cost)
                    continue

                intensity_difference = (
                    self._region_intensity_difference(
                        previous, region
                    )
                )

                shape_penalty = (
                    0.0 if shape_distance is None
                    else shape_distance
                )

                intensity_penalty = (
                    self.intensity_weight_km
                    * intensity_difference
                )

                tie_breaker = (
                    track_index * region_count + region_index
                ) * 1e-10

                row.append(
                    distance
                    + shape_penalty
                    + intensity_penalty
                    + tie_breaker
                )

            # Dummy columns allow a track to remain unmatched.
            row.extend([unmatched_cost] * track_count)
            costs.append(row)

        assignment = self._hungarian(costs)
        matches = {}

        for track_index, column_index in enumerate(assignment):
            if not 0 <= column_index < region_count:
                continue

            if costs[track_index][column_index] >= unmatched_cost:
                continue

            matches[track_index] = column_index

        return matches

    @staticmethod
    def _hungarian(cost_matrix):
        """Rectangular Hungarian algorithm; columns must be >= rows."""

        n = len(cost_matrix)

        if n == 0:
            return []

        m = len(cost_matrix[0])

        if m < n:
            raise ValueError(
                "Hungarian assignment requires columns >= rows."
            )

        if any(len(row) != m for row in cost_matrix):
            raise ValueError("Cost matrix must be rectangular.")

        u = [0.0] * (n + 1)
        v = [0.0] * (m + 1)
        p = [0] * (m + 1)
        way = [0] * (m + 1)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [float("inf")] * (m + 1)
            used = [False] * (m + 1)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float("inf")
                j1 = 0

                for j in range(1, m + 1):
                    if used[j]:
                        continue

                    current = (
                        cost_matrix[i0 - 1][j - 1]
                        - u[i0] - v[j]
                    )

                    if current < minv[j]:
                        minv[j] = current
                        way[j] = j0

                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

                for j in range(m + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1

                if p[j0] == 0:
                    break

            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1

                if j0 == 0:
                    break

        assignment = [-1] * n

        for j in range(1, m + 1):
            if p[j] != 0:
                assignment[p[j] - 1] = j - 1

        return assignment

    # ---------------------------------------------------------
    # Geographic and region helpers
    # ---------------------------------------------------------

    @staticmethod
    def _region_centroid(region):
        latitude = getattr(region, "centroid_latitude", None)
        longitude = getattr(region, "centroid_longitude", None)

        if latitude is None:
            latitude = (
                region.min_latitude + region.max_latitude
            ) / 2.0

        if longitude is None:
            longitude = (
                region.min_longitude + region.max_longitude
            ) / 2.0

        latitude = float(latitude)
        longitude = float(longitude)

        if (
            not np.isfinite(latitude)
            or not -90.0 <= latitude <= 90.0
        ):
            raise ValueError(
                "Region centroid latitude must be in [-90, 90]."
            )

        if not np.isfinite(longitude):
            raise ValueError(
                "Region centroid longitude must be finite."
            )

        return latitude, (longitude + 180.0) % 360.0 - 180.0

    @staticmethod
    def _wrapped_longitude_difference(first, second):
        return (second - first + 180.0) % 360.0 - 180.0

    @staticmethod
    def _time_seconds(value):
        if isinstance(value, datetime):
            if value.tzinfo is not None:
                return value.timestamp()

            return (
                value - datetime(1970, 1, 1)
            ).total_seconds()

        try:
            timestamp = np.datetime64(value, "ns")

            if np.isnat(timestamp):
                raise ValueError("Timestamp cannot be NaT.")

            return float(
                timestamp.astype("int64")
            ) / 1_000_000_000.0

        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                f"Unsupported or invalid timestamp: {value!r}"
            ) from error

    @staticmethod
    def _create_track(track_id, region):
        track = WeatherAnomalyTrack(
            track_id=track_id,
            category=region.category,
        )
        track.add_region(region)
        return track

    @staticmethod
    def _region_coordinates(region):
        coordinates = []

        for record in region.node_records:
            latitude = float(record["latitude"])
            longitude = float(record["longitude"])

            if (
                not np.isfinite(latitude)
                or not -90.0 <= latitude <= 90.0
            ):
                raise ValueError(
                    "Node latitude must be in [-90, 90]."
                )

            if not np.isfinite(longitude):
                raise ValueError("Node longitude must be finite.")

            longitude = (longitude + 180.0) % 360.0 - 180.0
            coordinates.append((latitude, longitude))

        return coordinates

    @classmethod
    def _coordinate_distance_km(cls, first, second):
        """Great-circle distance between coordinate pairs."""

        lat1, lon1 = first
        lat2, lon2 = second

        lat1 = radians(lat1)
        lat2 = radians(lat2)

        delta_lat = lat2 - lat1
        delta_lon = radians(
            (lon2 - lon1 + 180.0) % 360.0 - 180.0
        )

        haversine = (
            sin(delta_lat / 2.0) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2.0) ** 2
        )

        haversine = min(1.0, max(0.0, haversine))

        return (
            2.0 * cls.EARTH_RADIUS_KM
            * asin(sqrt(haversine))
        )

    def _region_shape_distance_km(self, first_region, second_region):
        """
        Symmetric mean nearest-neighbor distance between samples.

        This is a shape-similarity proxy, not exact polygon overlap.
        """

        first = self._region_coordinates(first_region)
        second = self._region_coordinates(second_region)

        if len(first) < 2 or len(second) < 2:
            return None

        def directed_mean_nearest(source, target):
            return float(np.mean([
                min(
                    self._coordinate_distance_km(point, other)
                    for other in target
                )
                for point in source
            ]))

        return (
            directed_mean_nearest(first, second)
            + directed_mean_nearest(second, first)
        ) / 2.0

    @staticmethod
    def _region_intensity_difference(first_region, second_region):
        """Normalized difference between absolute mean anomalies."""

        first_value = first_region.mean_standardized_anomaly
        second_value = second_region.mean_standardized_anomaly

        if first_value is None or second_value is None:
            return 0.0

        first_value = abs(float(first_value))
        second_value = abs(float(second_value))

        if (
            not np.isfinite(first_value)
            or not np.isfinite(second_value)
        ):
            return 0.0

        difference = abs(first_value - second_value)
        scale = max(first_value, second_value, 1.0)

        return min(1.0, difference / scale)
