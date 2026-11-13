
from math import isclose

from weather.weather_anomaly_region import WeatherAnomalyRegion


print("Weather Anomaly Region test")
print()

region = WeatherAnomalyRegion(
    region_id=0,
    time="2015-01-01T00:00:00",
    category="extreme_heat"
)

region.add_node(
    node_id=38,
    latitude=20.0,
    longitude=78.5,
    value=30.0,
    standardized_anomaly=2.5
)

region.add_node(
    node_id=39,
    latitude=20.5,
    longitude=79.0,
    value=34.0,
    standardized_anomaly=3.5
)

print("Region information")
print("------------------")
print("Region ID:", region.region_id)
print("Category:", region.category)
print("Timestamp:", region.time)
print("Node IDs:", region.node_ids)
print("Node count:", region.node_count)

print()
print("Geographic statistics")
print("---------------------")
print("Latitude bounds:", region.min_latitude, region.max_latitude)
print("Longitude bounds:", region.min_longitude, region.max_longitude)
print("Latitude span:", region.latitude_span)
print("Longitude span:", region.longitude_span)
print("Centroid latitude:", region.centroid_latitude)
print("Centroid longitude:", region.centroid_longitude)

print()
print("Weather statistics")
print("------------------")
print("Minimum:", region.min_value)
print("Maximum:", region.max_value)
print("Mean:", region.mean_value)
print("Minimum standardized anomaly:", region.min_standardized_anomaly)
print("Maximum standardized anomaly:", region.max_standardized_anomaly)
print("Mean standardized anomaly:", region.mean_standardized_anomaly)

print()
print("Peak anomaly")
print("------------")
print("Peak node:", region.peak_node_id)
print("Peak latitude:", region.peak_latitude)
print("Peak longitude:", region.peak_longitude)

print()
print("Approximate spatial area")
print("------------------------")
print("Area (km²):", region.approximate_area_km2)

print()
print("Node records")
print("------------")
for node in region.node_records:
    print(node)

# ---------------------------------------------------------
# Assertions
# ---------------------------------------------------------

assert region.node_count == 2
assert region.node_ids == [38, 39]

assert isclose(region.min_value, 30.0)
assert isclose(region.max_value, 34.0)
assert isclose(region.mean_value, 32.0)

assert isclose(region.centroid_latitude, 20.25)
assert isclose(region.centroid_longitude, 78.75)

assert isclose(region.min_standardized_anomaly, 2.5)
assert isclose(region.max_standardized_anomaly, 3.5)
assert isclose(region.mean_standardized_anomaly, 3.0)

assert region.peak_node_id == 39
assert region.peak_latitude == 20.5
assert region.peak_longitude == 79.0

assert region.approximate_area_km2 > 0

# Duplicate nodes must not affect statistics.
region.add_node(
    node_id=39,
    latitude=20.5,
    longitude=79.0,
    value=999.0,
    standardized_anomaly=10.0
)

assert region.node_count == 2
assert isclose(region.mean_value, 32.0)

print()
print("All Weather Anomaly Region tests passed.")
