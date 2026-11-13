
from weather.weather_anomaly_region import WeatherAnomalyRegion
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker


def create_region(region_id, time, latitude, longitude):
    region = WeatherAnomalyRegion(
        region_id=region_id,
        time=time,
        category="extreme_heat",
    )

    region.add_node(
        node_id=region_id,
        latitude=latitude,
        longitude=longitude,
        value=35.0,
        standardized_anomaly=3.0,
    )

    return region


def make_field(time, *regions):
    return {"time": time, "regions": list(regions)}


def region_ids(track):
    return [region.region_id for region in track.regions]


# Test 1: reconnect after one missing observation.
tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
    max_missed_observations=1,
)

tracks = tracker.build_tracks([
    make_field(
        "2015-01-01T00:00:00",
        create_region(0, "2015-01-01T00:00:00", 20.0, 78.0),
    ),
    make_field("2015-01-01T06:00:00"),
    make_field(
        "2015-01-01T12:00:00",
        create_region(1, "2015-01-01T12:00:00", 20.0, 78.5),
    ),
])

assert len(tracks) == 1
assert region_ids(tracks[0]) == [0, 1]
print("PASS: track reconnects after one empty observation.")


# Test 2: max_missed_observations=0 disables gap bridging.
tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
    max_missed_observations=0,
)

tracks = tracker.build_tracks([
    make_field(
        "2015-01-01T00:00:00",
        create_region(10, "2015-01-01T00:00:00", 20.0, 78.0),
    ),
    make_field("2015-01-01T06:00:00"),
    make_field(
        "2015-01-01T12:00:00",
        create_region(11, "2015-01-01T12:00:00", 20.0, 78.5),
    ),
])

assert len(tracks) == 2
assert region_ids(tracks[0]) == [10]
assert region_ids(tracks[1]) == [11]
print("PASS: expired track does not reconnect when allowance is zero.")


# Test 3: two consecutive empty observations expire a track
# when the allowance is one.
tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
    max_missed_observations=1,
)

tracks = tracker.build_tracks([
    make_field(
        "2015-01-01T00:00:00",
        create_region(20, "2015-01-01T00:00:00", 20.0, 78.0),
    ),
    make_field("2015-01-01T06:00:00"),
    make_field("2015-01-01T12:00:00"),
    make_field(
        "2015-01-01T18:00:00",
        create_region(21, "2015-01-01T18:00:00", 20.0, 78.5),
    ),
])

assert len(tracks) == 2
assert region_ids(tracks[0]) == [20]
assert region_ids(tracks[1]) == [21]
print("PASS: track expires after exceeding its missed-observation allowance.")


# Test 4: elapsed-time-aware matching scales the distance threshold.
tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
    max_missed_observations=1,
)

normal_limit = tracker._maximum_match_distance(6.0)
gap_limit = tracker._maximum_match_distance(12.0)
over_limit = tracker._maximum_match_distance(18.0)

assert normal_limit == 300.0
assert gap_limit == 600.0
assert over_limit == 600.0
print("PASS: distance threshold scales with elapsed time and is capped.")


# Test 5: original input dictionaries are not modified.
first_field = make_field(
    "2015-01-01T00:00:00",
    create_region(30, "2015-01-01T00:00:00", 20.0, 78.0),
)
original_regions = first_field["regions"].copy()

tracker.build_tracks([first_field])

assert first_field["regions"] == original_regions
print("PASS: caller's input fields remain unchanged.")

print("\nAll gap-bridging tests passed.")
