
from weather.weather_anomaly_region import WeatherAnomalyRegion
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker


def create_region(region_id, latitude, longitude):
    region = WeatherAnomalyRegion(
        region_id=region_id,
        time="2015-01-01T00:00:00",
        category="extreme_heat",
    )

    region.add_node(
        node_id=region_id,
        latitude=latitude,
        longitude=longitude,
        value=30.0,
        standardized_anomaly=3.0,
    )

    return region


tracker = AnomalyTemporalTracker(maximum_distance_km=300.0)

# Approximately 52 km apart at latitude 20 degrees.
first = create_region(0, 20.0, 78.5)
second = create_region(1, 20.0, 79.0)

distance = tracker.region_distance_km(first, second)
assert 50.0 < distance < 55.0, distance

# Across the antimeridian, the points are only about 22 km apart.
west = create_region(2, 0.0, 179.9)
east = create_region(3, 0.0, -179.9)

antimeridian_distance = tracker.region_distance_km(west, east)
assert 20.0 < antimeridian_distance < 23.0, antimeridian_distance

# Category must not influence the distance calculation itself;
# category filtering belongs to the matching stage.
print(f"Ordinary distance: {distance:.2f} km")
print(f"Antimeridian distance: {antimeridian_distance:.2f} km")
print("Geographic distance tests passed.")
