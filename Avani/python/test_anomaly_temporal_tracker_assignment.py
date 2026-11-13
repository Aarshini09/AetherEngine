
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


tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
)

# Two tracks at the first observation.
track_a_region = create_region(
    0, "2015-01-01T00:00:00", 20.0, 78.0
)
track_b_region = create_region(
    1, "2015-01-01T00:00:00", 20.0, 80.0
)

# At the next observation, region 2 is relatively close to both
# tracks, while region 3 is much closer to track A.
#
# A greedy assignment can make a locally good choice that prevents
# the globally best pairing.
next_region_2 = create_region(
    2, "2015-01-01T06:00:00", 20.0, 79.0
)
next_region_3 = create_region(
    3, "2015-01-01T06:00:00", 20.0, 77.0
)

tracks = tracker.build_tracks([
    {
        "time": "2015-01-01T00:00:00",
        "regions": [track_a_region, track_b_region],
    },
    {
        "time": "2015-01-01T06:00:00",
        "regions": [next_region_2, next_region_3],
    },
])

for track in tracks:
    region_ids = [region.region_id for region in track.regions]
    print(f"Track {track.track_id}: regions={region_ids}")

# Every region must belong to exactly one track.
all_region_ids = [
    region.region_id
    for track in tracks
    for region in track.regions
]

assert len(all_region_ids) == len(set(all_region_ids)), (
    "A region was assigned to multiple tracks."
)

assert set(all_region_ids) == {0, 1, 2, 3}, (
    "A region was lost or an unexpected region was added."
)

# Both tracks should continue, rather than spawning duplicates.
assert len(tracks) == 2, (
    f"Expected 2 tracks, got {len(tracks)}."
)

assert all(len(track.regions) == 2 for track in tracks), (
    "Each track should contain one region from each observation."
)

print("Global assignment validation passed.")
