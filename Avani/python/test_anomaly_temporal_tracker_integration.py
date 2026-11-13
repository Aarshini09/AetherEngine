
from datetime import datetime, timedelta

from weather.anomaly_temporal_tracker import AnomalyTemporalTracker
from weather.weather_anomaly_region import WeatherAnomalyRegion


T0 = datetime(2020, 1, 1, 0, 0)
T1 = T0 + timedelta(hours=6)
T2 = T0 + timedelta(hours=12)
T3 = T0 + timedelta(hours=18)


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
            value=35.0,
            standardized_anomaly=intensity,
        )

    return region


def square(south, west, step=0.1):
    return [
        (south, west),
        (south, west + step),
        (south + step, west),
        (south + step, west + step),
    ]


def build_observation(time, regions):
    return {"time": time, "regions": regions}


def run_integration_test():
    tracker = AnomalyTemporalTracker(
        maximum_distance_km=300.0,
        expected_interval_hours=6.0,
        max_missed_observations=1,
        maximum_shape_distance_km=150.0,
        intensity_weight_km=50.0,
    )

    # Observation 0: one heat anomaly.
    initial = make_region(
        0, T0, square(20.0, 78.0)
    )

    # Observation 1: the same anomaly moves northeast.
    moved = make_region(
        1, T1, square(20.1, 78.1)
    )

    # Observation 2: the main anomaly splits into two.
    child_a = make_region(
        2,
        T2,
        [
            (20.1, 78.1),
            (20.1, 78.15),
            (20.15, 78.1),
            (20.15, 78.15),
        ],
    )

    child_b = make_region(
        3,
        T2,
        [
            (20.15, 78.15),
            (20.15, 78.2),
            (20.2, 78.15),
            (20.2, 78.2),
        ],
    )

    # A nearby but spatially distinct anomaly.
    # Its centroid is within the broad distance threshold,
    # but its shape should fail the tighter shape gate.
    unrelated = make_region(
        4, T2, square(22.5, 78.1)
    )

    # Observation 3: the two branches merge into one region.
    merged = make_region(
        5,
        T3,
        [
            (20.1, 78.1),
            (20.1, 78.15),
            (20.1, 78.2),
            (20.15, 78.1),
            (20.15, 78.15),
            (20.15, 78.2),
            (20.2, 78.1),
            (20.2, 78.15),
            (20.2, 78.2),
        ],
    )

    unrelated_later = make_region(
        6, T3, square(22.5, 78.1)
    )

    fields = [
        build_observation(T0, [initial]),
        build_observation(T1, [moved]),
        build_observation(T2, [child_a, child_b, unrelated]),
        build_observation(T3, [merged, unrelated_later]),
    ]

    tracks = tracker.build_tracks(fields)

    print("\nIntegrated anomaly lifecycle test")
    print("=" * 40)

    for track in tracks:
        region_ids = [
            region.region_id for region in track.regions
        ]

        print(f"\nTrack {track.track_id}")
        print(f"  Category: {track.category}")
        print(f"  Region IDs: {region_ids}")
        print(f"  Parent tracks: {track.parent_track_ids}")
        print(f"  Child tracks: {track.child_track_ids}")
        print(f"  Merged from: {track.merged_from_track_ids}")
        print(f"  Merged into: {track.merged_into_track_ids}")

    # Locate tracks by the regions they contain.
    def track_containing(region_id):
        matches = [
            track
            for track in tracks
            if any(
                region.region_id == region_id
                for region in track.regions
            )
        ]

        assert len(matches) == 1, (
            f"Expected exactly one track containing region "
            f"{region_id}; got {len(matches)}."
        )

        return matches[0]

    original_track = track_containing(0)
    moved_track = track_containing(1)
    child_a_track = track_containing(2)
    child_b_track = track_containing(3)
    unrelated_track = track_containing(4)
    merged_track = track_containing(5)
    unrelated_later_track = track_containing(6)

    # 1. Movement: the original anomaly remains continuous.
    assert original_track.track_id == moved_track.track_id
    print("\nPASS: moving anomaly retains its track identity.")

    # 2. Split: the two branches belong to distinct tracks.
    assert child_a_track.track_id != child_b_track.track_id

    split_parent = (
        child_a_track
        if child_a_track.track_id == original_track.track_id
        else child_b_track
    )

    new_child = (
        child_b_track
        if child_a_track.track_id == original_track.track_id
        else child_a_track
    )

    assert split_parent.track_id == original_track.track_id
    assert original_track.track_id in new_child.parent_track_ids
    assert new_child.track_id in original_track.child_track_ids

    print("PASS: split creates a child track with parent metadata.")

    # 3. Nearby unrelated anomaly must remain independent.
    assert unrelated_track.track_id != original_track.track_id
    assert unrelated_later_track.track_id == unrelated_track.track_id

    print("PASS: nearby unrelated anomaly remains independent.")

    # 4. Merge: one branch survives; the other ends in a merge.
    assert merged_track.track_id in {
        child_a_track.track_id,
        child_b_track.track_id,
    }

    merged_away_tracks = [
        track
        for track in (child_a_track, child_b_track)
        if track.track_id != merged_track.track_id
    ]

    assert len(merged_away_tracks) == 1
    merged_away = merged_away_tracks[0]

    assert (
        merged_away.track_id
        in merged_track.merged_from_track_ids
    )
    assert (
        merged_track.track_id
        in merged_away.merged_into_track_ids
    )

    print("PASS: merge records survivor and merged-away track.")

    # The unrelated event must not be absorbed during the merge.
    assert unrelated_later_track.track_id != merged_track.track_id

    print("PASS: merge does not absorb the unrelated event.")

    print("\nAll integrated lifecycle assertions passed.")


if __name__ == "__main__":
    run_integration_test()
