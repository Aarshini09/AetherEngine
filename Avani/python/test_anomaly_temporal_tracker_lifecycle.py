
from datetime import datetime, timedelta, timezone

from weather.anomaly_temporal_tracker import AnomalyTemporalTracker
from weather.weather_anomaly_region import WeatherAnomalyRegion


T0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
T1 = T0 + timedelta(hours=6)



def make_region(region_id, time, points, intensity=3.0):
    region = WeatherAnomalyRegion(
        region_id=region_id,
        time=time,
        category="extreme_heat",
    )

    for index, (latitude, longitude) in enumerate(points):
        region.add_node(
            node_id=region_id * 100 + index,
            latitude=latitude,
            longitude=longitude,
            value=30.0,
            standardized_anomaly=intensity,
        )

    return region



def test_split_relationship():
    tracker = AnomalyTemporalTracker(
        maximum_distance_km=300,
        maximum_shape_distance_km=150,
        max_missed_observations=1,
    )

    parent = make_region(
        0, T0,
        [(20.0, 78.0), (20.0, 78.1),
         (20.1, 78.0), (20.1, 78.1)],
    )

    # Two smaller regions within the parent region's neighborhood.
    child_a = make_region(
        1, T1,
        [(20.0, 78.0), (20.0, 78.05),
         (20.05, 78.0), (20.05, 78.05)],
    )
    child_b = make_region(
        2, T1,
        [(20.05, 78.05), (20.05, 78.1),
         (20.1, 78.05), (20.1, 78.1)],
    )

    tracks = tracker.build_tracks([
        {"time": T0, "regions": [parent]},
        {"time": T1, "regions": [child_a, child_b]},
    ])

    assert len(tracks) == 2, len(tracks)

    parent_track = next(
        track for track in tracks if track.track_id == 0
    )
    child_track = next(
        track for track in tracks if track.track_id == 1
    )

    assert parent_track.region_count == 2
    assert child_track.region_count == 1
    assert child_track.parent_track_ids == {parent_track.track_id}
    assert child_track.track_id in parent_track.child_track_ids

    print("PASS: split relationship recorded.")


def test_merge_relationship():
    tracker = AnomalyTemporalTracker(
        maximum_distance_km=300,
        maximum_shape_distance_km=150,
        max_missed_observations=1,
    )

    first = make_region(
        10, T0,
        [(20.0, 78.0), (20.0, 78.1),
         (20.1, 78.0), (20.1, 78.1)],
    )
    second = make_region(
        11, T0,
        [(20.0, 78.0), (20.0, 78.1),
         (20.1, 78.0), (20.1, 78.1)],
    )
    merged = make_region(
        12, T1,
        [(20.0, 78.0), (20.0, 78.1),
         (20.1, 78.0), (20.1, 78.1)],
    )

    tracks = tracker.build_tracks([
        {"time": T0, "regions": [first, second]},
        {"time": T1, "regions": [merged]},
    ])

    assert len(tracks) == 2, len(tracks)

    survivor = next(
        track for track in tracks
        if track.region_count == 2
    )
    ended = next(
        track for track in tracks
        if track.region_count == 1
    )

    assert ended.track_id in survivor.merged_from_track_ids
    assert survivor.track_id in ended.merged_into_track_ids
    assert ended.track_id not in {
        entry["track"].track_id
        for entry in []
    }

    print("PASS: merge relationship recorded.")


if __name__ == "__main__":
    test_split_relationship()
    test_merge_relationship()
    print("\nAll lifecycle tests passed.")
