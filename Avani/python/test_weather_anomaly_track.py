
from math import isclose

from weather.weather_anomaly_track import WeatherAnomalyTrack
from weather.weather_anomaly_region import WeatherAnomalyRegion


print("Weather Anomaly Track test")
print()

# ---------------------------------------------------------
# Create two anomaly regions
# ---------------------------------------------------------

region_0 = WeatherAnomalyRegion(
    region_id=0,
    time="2015-01-01T00:00:00",
    category="extreme_heat"
)

region_0.add_node(
    node_id=38,
    latitude=20.0,
    longitude=78.5,
    value=20.9989,
    standardized_anomaly=2.0190
)

region_1 = WeatherAnomalyRegion(
    region_id=1,
    time="2015-01-01T06:00:00",
    category="extreme_heat"
)

region_1.add_node(
    node_id=40,
    latitude=20.0,
    longitude=79.0,
    value=21.0536,
    standardized_anomaly=2.0448
)

# ---------------------------------------------------------
# Create track
# ---------------------------------------------------------

track = WeatherAnomalyTrack(
    track_id=0,
    category="extreme_heat"
)

print("Initial track")
print("-------------")
print("Track ID:", track.track_id)
print("Category:", track.category)
print("Region count:", track.region_count)
print("Start time:", track.start_time)
print("End time:", track.end_time)

assert track.region_count == 0
assert track.start_time is None
assert track.end_time is None

# ---------------------------------------------------------
# Add regions
# ---------------------------------------------------------

track.add_region(region_0)
track.add_region(region_1)

print()
print("Track after adding regions")
print("--------------------------")
print("Track ID:", track.track_id)
print("Category:", track.category)
print("Region count:", track.region_count)
print("Start time:", track.start_time)
print("End time:", track.end_time)
print("Duration count:", track.duration_count)
print("Duration hours:", track.duration_hours)

# ---------------------------------------------------------
# Spatial movement and intensity
# ---------------------------------------------------------

print()
print("Track movement")
print("--------------")
print("Trajectory:", track.trajectory)
print("Displacement (km):", track.displacement_km)
print("Path length (km):", track.path_length_km)
print("Mean speed (km/h):", track.mean_speed_kmh)

print()
print("Track intensity")
print("---------------")
print("Peak |standardized anomaly|:", track.peak_standardized_anomaly)
print("Maximum approximate area (km²):", track.maximum_area_km2)

# ---------------------------------------------------------
# Inspect regions
# ---------------------------------------------------------

print()
print("Track regions")
print("-------------")

for index, region in enumerate(track.regions):
    print(f"Region {index}:")
    print("  Region ID:", region.region_id)
    print("  Time:", region.time)
    print("  Category:", region.category)
    print("  Nodes:", region.node_ids)
    print("  Centroid:", (
        region.centroid_latitude,
        region.centroid_longitude
    ))

# ---------------------------------------------------------
# Test region access
# ---------------------------------------------------------

first_region = track.get_region(0)
last_region = track.get_last_region()

assert first_region.region_id == 0
assert last_region.region_id == 1

print()
print("Region access passed.")

# ---------------------------------------------------------
# Test incompatible category
# ---------------------------------------------------------

invalid_region = WeatherAnomalyRegion(
    region_id=2,
    time="2015-01-01T12:00:00",
    category="extreme_cold"
)

invalid_region.add_node(
    node_id=50,
    latitude=20.0,
    longitude=80.0,
    value=10.0,
    standardized_anomaly=-2.5
)

try:
    track.add_region(invalid_region)
except ValueError:
    print("Category protection passed.")
else:
    raise AssertionError(
        "Track accepted an incompatible region."
    )

# ---------------------------------------------------------
# Test chronological order
# ---------------------------------------------------------

out_of_order_region = WeatherAnomalyRegion(
    region_id=3,
    time="2014-12-31T18:00:00",
    category="extreme_heat"
)

out_of_order_region.add_node(
    node_id=51,
    latitude=20.0,
    longitude=78.0,
    value=20.0,
    standardized_anomaly=2.1
)

try:
    track.add_region(out_of_order_region)
except ValueError:
    print("Chronological order protection passed.")
else:
    raise AssertionError(
        "Track accepted an out-of-order region."
    )

# ---------------------------------------------------------
# Scientific assertions
# ---------------------------------------------------------

assert track.region_count == 2
assert track.duration_count == 2

# Two observations six hours apart mean six elapsed hours.
assert isclose(track.duration_hours, 6.0)

assert track.displacement_km > 0
assert track.path_length_km > 0
assert track.mean_speed_kmh is not None
assert track.mean_speed_kmh > 0

assert isclose(
    track.peak_standardized_anomaly,
    2.0448
)

assert len(track.trajectory) == 2

print()
print("All Weather Anomaly Track tests passed.")
