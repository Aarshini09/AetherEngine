from weather.weather_anomaly_region import (
    WeatherAnomalyRegion
)

from weather.anomaly_temporal_tracker import (
    AnomalyTemporalTracker
)


def create_region(
    region_id,
    time,
    category,
    latitude,
    longitude,
    value=25.0,
    standardized_anomaly=3.0
):
    """
    Create a small anomaly region containing one node.

    The helper keeps the test focused on temporal tracking
    rather than anomaly-field construction.
    """

    region = WeatherAnomalyRegion(
        region_id=region_id,
        time=time,
        category=category
    )

    region.add_node(
        node_id=region_id,
        latitude=latitude,
        longitude=longitude,
        value=value,
        standardized_anomaly=standardized_anomaly
    )

    return region


print("Anomaly Temporal Tracker test")
print()


# =========================================================
# Timestamp T0
# =========================================================

region_t0_heat = create_region(
    region_id=0,
    time="2015-01-01T00:00:00",
    category="extreme_heat",
    latitude=20.0,
    longitude=78.0
)


# =========================================================
# Timestamp T1
# =========================================================

# This region has moved slightly east.
# It should continue the T0 heat track.

region_t1_heat = create_region(
    region_id=1,
    time="2015-01-01T06:00:00",
    category="extreme_heat",
    latitude=20.1,
    longitude=78.2
)


# New heat region.
# It is far enough away that it should create a new track.

region_t1_new_heat = create_region(
    region_id=2,
    time="2015-01-01T06:00:00",
    category="extreme_heat",
    latitude=25.0,
    longitude=85.0
)


# Cold anomaly at the same general location as the
# continuing heat anomaly.
#
# It must NOT be merged with the heat track because
# the categories are different.

region_t1_cold = create_region(
    region_id=3,
    time="2015-01-01T06:00:00",
    category="extreme_cold",
    latitude=20.1,
    longitude=78.2,
    value=5.0,
    standardized_anomaly=-3.0
)


# =========================================================
# Timestamp T2
# =========================================================

# Continue the original heat anomaly.

region_t2_heat = create_region(
    region_id=4,
    time="2015-01-01T12:00:00",
    category="extreme_heat",
    latitude=20.2,
    longitude=78.4
)


# Continue the cold anomaly.

region_t2_cold = create_region(
    region_id=5,
    time="2015-01-01T12:00:00",
    category="extreme_cold",
    latitude=20.2,
    longitude=78.4,
    value=4.0,
    standardized_anomaly=-3.2
)


# =========================================================
# Build temporal fields
# =========================================================

region_fields = [
    {
        "time": "2015-01-01T00:00:00",
        "regions": [
            region_t0_heat
        ]
    },

    {
        "time": "2015-01-01T06:00:00",
        "regions": [
            region_t1_heat,
            region_t1_new_heat,
            region_t1_cold
        ]
    },

    {
        "time": "2015-01-01T12:00:00",
        "regions": [
            region_t2_heat,
            region_t2_cold
        ]
    }
]


# =========================================================
# Create tracker
# =========================================================

tracker = AnomalyTemporalTracker(
    maximum_distance_km=300.0,
    expected_interval_hours=6.0,
)


# =========================================================
# Build tracks
# =========================================================

tracks = tracker.build_tracks(
    region_fields
)


# =========================================================
# Display results
# =========================================================

print("Temporal tracking results")
print("-------------------------")

print(
    "Number of tracks:",
    len(tracks)
)

print()


for track in tracks:

    print(
        f"Track {track.track_id}"
    )

    print(
        f"  Category: {track.category}"
    )

    print(
        f"  Region count: {track.region_count}"
    )

    print(
        f"  Start time: {track.start_time}"
    )

    print(
        f"  End time: {track.end_time}"
    )

    print(
        "  Regions:"
    )

    for region in track.regions:

        print(
            f"    Region {region.region_id} "
            f"at {region.time} "
            f"({region.category})"
        )

    print()


# =========================================================
# Validate expected result
# =========================================================

print("Validation")
print("----------")


# We expect:
#
# Track 0:
#   T0 heat region 0
#   T1 heat region 1
#   T2 heat region 4
#
# Track 1:
#   T1 new heat region 2
#
# Track 2:
#   T1 cold region 3
#   T2 cold region 5
#
# Therefore:
#
# Total tracks = 3

if len(tracks) != 3:
    raise RuntimeError(
        f"Expected 3 tracks, got {len(tracks)}."
    )


# ---------------------------------------------------------
# Validate first track
# ---------------------------------------------------------

track_0 = tracks[0]

if track_0.category != "extreme_heat":
    raise RuntimeError(
        "Track 0 category is incorrect."
    )

if track_0.region_count != 3:
    raise RuntimeError(
        "Track 0 should contain 3 regions."
    )

if [
    region.region_id
    for region in track_0.regions
] != [0, 1, 4]:

    raise RuntimeError(
        "Track 0 region sequence is incorrect."
    )


# ---------------------------------------------------------
# Validate second track
# ---------------------------------------------------------

track_1 = tracks[1]

if track_1.category != "extreme_heat":
    raise RuntimeError(
        "Track 1 category is incorrect."
    )

if track_1.region_count != 1:
    raise RuntimeError(
        "Track 1 should contain exactly 1 region."
    )

if track_1.regions[0].region_id != 2:
    raise RuntimeError(
        "Track 1 should contain region 2."
    )


# ---------------------------------------------------------
# Validate cold track
# ---------------------------------------------------------

track_2 = tracks[2]

if track_2.category != "extreme_cold":
    raise RuntimeError(
        "Track 2 category is incorrect."
    )

if track_2.region_count != 2:
    raise RuntimeError(
        "Track 2 should contain 2 regions."
    )

if [
    region.region_id
    for region in track_2.regions
] != [3, 5]:

    raise RuntimeError(
        "Track 2 region sequence is incorrect."
    )


# ---------------------------------------------------------
# Verify category separation
# ---------------------------------------------------------

if track_0.category == track_2.category:
    raise RuntimeError(
        "Heat and cold anomalies were incorrectly merged."
    )


print("Track count:       PASS")
print("Heat movement:     PASS")
print("New event:         PASS")
print("Category separation: PASS")
print("Track sequences:   PASS")

print()
print("Anomaly Temporal Tracker test complete.")