
from weather.weather_anomaly_region import WeatherAnomalyRegion
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker


def make_region(region_id, time, coordinates, anomaly):
    region = WeatherAnomalyRegion(
        region_id=region_id,
        time=time,
        category="extreme_heat",
    )

    for index, (latitude, longitude) in enumerate(coordinates):
        region.add_node(
            node_id=region_id * 100 + index,
            latitude=latitude,
            longitude=longitude,
            value=35.0,
            standardized_anomaly=anomaly,
        )

    return region


tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
    max_missed_observations=1,
    maximum_shape_distance_km=150.0,
    intensity_weight_km=50.0,
)


# ---------------------------------------------------------
# Test 1: Prefer the matching shape when centroids coincide
# ---------------------------------------------------------

base_shape = [
    (20.0, 78.0),
    (20.0, 78.1),
    (20.1, 78.0),
    (20.1, 78.1),
]

# Same centroid, but a much more spatially dispersed footprint.
different_shape = [
    (18.0, 76.0),
    (18.0, 80.0),
    (22.0, 76.0),
    (22.0, 80.0),
]

previous = make_region(
    1, "2015-01-01T00:00:00", base_shape, 3.0
)
matching_candidate = make_region(
    2, "2015-01-01T06:00:00", base_shape, 3.0
)
different_candidate = make_region(
    3, "2015-01-01T06:00:00", different_shape, 3.0
)

track = tracker._create_track(0, previous)

matches = tracker._match_regions(
    [track],
    [different_candidate, matching_candidate],
    current_time="2015-01-01T06:00:00",
)

assert matches == {0: 1}, (
    f"Expected the matching shape at index 1, got {matches}"
)

print("PASS: matching favors geographic shape over candidate order.")


# ---------------------------------------------------------
# Test 2: Intensity evidence resolves a competing assignment
# ---------------------------------------------------------

track_weak = tracker._create_track(
    10,
    make_region(10, "2015-01-01T00:00:00", base_shape, 2.0),
)
track_strong = tracker._create_track(
    11,
    make_region(11, "2015-01-01T00:00:00", base_shape, 5.0),
)

candidate_weak = make_region(
    12, "2015-01-01T06:00:00", base_shape, 2.0
)
candidate_strong = make_region(
    13, "2015-01-01T06:00:00", base_shape, 5.0
)

matches = tracker._match_regions(
    [track_weak, track_strong],
    [candidate_strong, candidate_weak],
    current_time="2015-01-01T06:00:00",
)

assert matches == {0: 1, 1: 0}, (
    f"Expected intensity-consistent assignment, got {matches}"
)

print("PASS: intensity evidence resolves competing assignments.")

print("\nAll integrated matching-evidence tests passed.")
