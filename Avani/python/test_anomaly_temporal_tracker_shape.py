
from weather.weather_anomaly_region import WeatherAnomalyRegion
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker


def create_region(region_id, time, coordinates, anomaly=3.0):
    """Create a region with independently specified coordinate samples."""

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


tracker = AnomalyTemporalTracker()


# ---------------------------------------------------------
# Test 1: Same shape, different node IDs
# ---------------------------------------------------------

shape_a = [
    (20.0, 78.0),
    (20.0, 78.1),
    (20.1, 78.0),
    (20.1, 78.1),
]

shape_b = [
    (20.0, 78.0),
    (20.0, 78.1),
    (20.1, 78.0),
    (20.1, 78.1),
]

region_a = create_region(1, "2015-01-01T00:00:00", shape_a)
region_b = create_region(2, "2015-01-01T06:00:00", shape_b)

shape_distance = tracker._region_shape_distance_km(
    region_a, region_b
)

assert shape_distance is not None
assert shape_distance < 0.001

print("PASS: identical geographic shapes match independently of node IDs.")


# ---------------------------------------------------------
# Test 2: Similar central location, different shape
# ---------------------------------------------------------

compact_shape = [
    (19.95, 77.95),
    (19.95, 78.05),
    (20.05, 77.95),
    (20.05, 78.05),
]

elongated_shape = [
    (19.8, 78.0),
    (19.9, 78.0),
    (20.0, 78.0),
    (20.1, 78.0),
    (20.2, 78.0),
]

compact = create_region(
    3, "2015-01-01T00:00:00", compact_shape
)
elongated = create_region(
    4, "2015-01-01T06:00:00", elongated_shape
)

centroid_distance = tracker.region_distance_km(
    compact, elongated
)
shape_distance = tracker._region_shape_distance_km(
    compact, elongated
)

assert centroid_distance < 20.0
assert shape_distance is not None
assert shape_distance > 1.0

print("PASS: shape distance distinguishes different spatial distributions.")


# ---------------------------------------------------------
# Test 3: Intensity difference
# ---------------------------------------------------------

weak_region = create_region(
    5,
    "2015-01-01T00:00:00",
    shape_a,
    anomaly=2.0,
)

strong_region = create_region(
    6,
    "2015-01-01T06:00:00",
    shape_b,
    anomaly=5.0,
)

intensity_difference = tracker._region_intensity_difference(
    weak_region, strong_region
)

assert 0.0 < intensity_difference <= 1.0

identical_intensity_difference = (
    tracker._region_intensity_difference(
        weak_region,
        create_region(
            7,
            "2015-01-01T06:00:00",
            shape_b,
            anomaly=2.0,
        ),
    )
)

assert identical_intensity_difference == 0.0

print("PASS: intensity evidence distinguishes anomaly strengths.")


# ---------------------------------------------------------
# Test 4: Single-node regions
# ---------------------------------------------------------

single_a = create_region(
    8,
    "2015-01-01T00:00:00",
    [(20.0, 78.0)],
)

single_b = create_region(
    9,
    "2015-01-01T06:00:00",
    [(20.1, 78.1)],
)

assert tracker._region_shape_distance_km(
    single_a, single_b
) is None

assert tracker.region_distance_km(single_a, single_b) > 0.0

print("PASS: single-node regions fall back to centroid distance.")


# ---------------------------------------------------------
# Test 5: Antimeridian-crossing regions
# ---------------------------------------------------------

east_region = create_region(
    10,
    "2015-01-01T00:00:00",
    [
        (10.0, 179.8),
        (10.0, 179.9),
        (10.1, 179.8),
    ],
)

wrapped_region = create_region(
    11,
    "2015-01-01T06:00:00",
    [
        (10.0, -180.2),
        (10.0, -180.1),
        (10.1, -180.2),
    ],
)

antimeridian_shape_distance = tracker._region_shape_distance_km(
    east_region, wrapped_region
)

assert antimeridian_shape_distance is not None
assert antimeridian_shape_distance < 0.001

print("PASS: shape comparison handles longitude wrapping.")


# ---------------------------------------------------------
# Test 6: Direct coordinate distance
# ---------------------------------------------------------

distance = tracker._coordinate_distance_km(
    (20.0, 78.0),
    (20.0, 78.5),
)

assert 50.0 < distance < 55.0

print(f"PASS: direct coordinate distance = {distance:.2f} km.")
print("\nAll shape and intensity helper tests passed.")
