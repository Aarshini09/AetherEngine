from weather.weather_anomaly_region import (
    WeatherAnomalyRegion
)

from weather.weather_anomaly_track import (
    WeatherAnomalyTrack
)

from weather.weather_event import (
    WeatherEvent
)


def create_region(
    region_id,
    time,
    latitude,
    longitude,
    value,
    standardized_anomaly
):
    """
    Create a single-node extreme-heat anomaly region
    for the event test.
    """

    region = WeatherAnomalyRegion(
        region_id=region_id,
        time=time,
        category="extreme_heat"
    )

    region.add_node(
        node_id=region_id,
        latitude=latitude,
        longitude=longitude,
        value=value,
        standardized_anomaly=standardized_anomaly
    )

    return region


print("Weather Event test")
print()


# =========================================================
# Create anomaly regions
# =========================================================

region_0 = create_region(
    region_id=0,
    time="2015-01-01T00:00:00",
    latitude=20.0,
    longitude=78.0,
    value=25.0,
    standardized_anomaly=2.5
)


region_1 = create_region(
    region_id=1,
    time="2015-01-01T06:00:00",
    latitude=20.2,
    longitude=78.3,
    value=27.0,
    standardized_anomaly=3.2
)


region_2 = create_region(
    region_id=2,
    time="2015-01-01T12:00:00",
    latitude=20.4,
    longitude=78.6,
    value=29.0,
    standardized_anomaly=4.1
)


# =========================================================
# Build anomaly track
# =========================================================

track = WeatherAnomalyTrack(
    track_id=0,
    category="extreme_heat"
)

track.add_region(region_0)
track.add_region(region_1)
track.add_region(region_2)


print("Anomaly track")
print("-------------")

print(
    "Track ID:",
    track.track_id
)

print(
    "Category:",
    track.category
)

print(
    "Region count:",
    track.region_count
)

print(
    "Start time:",
    track.start_time
)

print(
    "End time:",
    track.end_time
)

print()


# =========================================================
# Create weather event
# =========================================================

event = WeatherEvent(
    event_id=0,
    category="extreme_heat",
    track=track
)


# =========================================================
# Display event
# =========================================================

print("Weather event")
print("-------------")

print(
    "Event ID:",
    event.event_id
)

print(
    "Category:",
    event.category
)

print(
    "Start time:",
    event.start_time
)

print(
    "End time:",
    event.end_time
)

print(
    "Region count:",
    event.region_count
)

print(
    "Duration steps:",
    event.duration_steps
)

print(
    "Start location:",
    event.start_location
)

print(
    "End location:",
    event.end_location
)

print(
    "Has movement:",
    event.has_movement
)

print(
    "Minimum value:",
    event.minimum_value
)

print(
    "Maximum value:",
    event.maximum_value
)

print(
    "Minimum z-score:",
    event.minimum_standardized_anomaly
)

print(
    "Maximum z-score:",
    event.maximum_standardized_anomaly
)

print(
    "Threat level:",
    event.threat_level
)

print()


# =========================================================
# Validation
# =========================================================

print("Validation")
print("----------")


if event.event_id != 0:
    raise RuntimeError(
        "Event ID is incorrect."
    )


if event.category != "extreme_heat":
    raise RuntimeError(
        "Event category is incorrect."
    )


if event.region_count != 3:
    raise RuntimeError(
        "Event should contain 3 regions."
    )


if event.start_time != "2015-01-01T00:00:00":
    raise RuntimeError(
        "Event start time is incorrect."
    )


if event.end_time != "2015-01-01T12:00:00":
    raise RuntimeError(
        "Event end time is incorrect."
    )


if event.start_location != (20.0, 78.0):
    raise RuntimeError(
        "Event start location is incorrect."
    )


if event.end_location != (20.4, 78.6):
    raise RuntimeError(
        "Event end location is incorrect."
    )


if not event.has_movement:
    raise RuntimeError(
        "Event movement was not detected."
    )


if event.minimum_value != 25.0:
    raise RuntimeError(
        "Minimum event value is incorrect."
    )


if event.maximum_value != 29.0:
    raise RuntimeError(
        "Maximum event value is incorrect."
    )


if event.minimum_standardized_anomaly != 2.5:
    raise RuntimeError(
        "Minimum standardized anomaly is incorrect."
    )


if event.maximum_standardized_anomaly != 4.1:
    raise RuntimeError(
        "Maximum standardized anomaly is incorrect."
    )


if event.threat_level != "unknown":
    raise RuntimeError(
        "Initial threat level should be unknown."
    )


print("Event ID:          PASS")
print("Category:           PASS")
print("Time range:         PASS")
print("Region count:       PASS")
print("Start location:     PASS")
print("End location:       PASS")
print("Movement detection: PASS")
print("Value range:        PASS")
print("Z-score range:      PASS")
print("Threat state:       PASS")

print()
print("Weather Event test complete.")