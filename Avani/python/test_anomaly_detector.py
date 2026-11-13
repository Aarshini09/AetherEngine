from config import ERA5_RAW_ROOT

from weather.era5_reader import ERA5Reader
from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor
)
from weather.anomaly_detector import AnomalyDetector


temperature_file = (
    ERA5_RAW_ROOT
    / "temperature_2015_2019.nc"
)


reader = ERA5Reader(
    temperature_file
)

reader.open()


processor = HistoricalBaselineProcessor(
    reader
)


baselines = processor.compute_point_baseline(
    variable_name="temperature",

    latitude=20.5937,
    longitude=78.9629,

    start_time="2015-01-01T00:00:00",
    end_time="2019-12-31T18:00:00"
)


baseline = baselines[
    (1, 0)
]


detector = AnomalyDetector(
    threshold=2.0
)


print("Weather Anomaly Detector test")
print()


print("January 00:00 baseline")
print(
    f"Mean: "
    f"{baseline.mean:.4f} "
    f"{baseline.unit}"
)

print(
    f"Std:  "
    f"{baseline.standard_deviation:.4f} "
    f"{baseline.unit}"
)

print()


# The original ERA5 observation:
#
# 293.61376953125 K
#
# Converted into application units:
#
# 20.46376953125 °C

normal_value = 20.46376953125


normal_anomaly = detector.detect(
    variable="temperature",

    time="2015-01-01T00:00:00",

    latitude=20.5937,
    longitude=78.9629,

    value=normal_value,

    baseline=baseline
)


print("Normal observation")
print()

print(
    f"Value:              "
    f"{normal_anomaly.value:.4f} "
    f"{baseline.unit}"
)

print(
    f"Absolute anomaly:   "
    f"{normal_anomaly.absolute_anomaly:.4f} "
    f"{baseline.unit}"
)

print(
    f"Standardized anomaly:"
    f" {normal_anomaly.standardized_anomaly:.4f}"
)

print(
    f"Is anomaly:         "
    f"{normal_anomaly.is_anomaly}"
)

print(
    f"Severity:           "
    f"{normal_anomaly.severity}"
)

print()


# Artificial extreme observation used only to
# verify anomaly classification.

extreme_value = (
    baseline.mean
    + (
        baseline.standard_deviation
        * 4.5
    )
)


extreme_anomaly = detector.detect(
    variable="temperature",

    time="2015-01-01T00:00:00",

    latitude=20.5937,
    longitude=78.9629,

    value=extreme_value,

    baseline=baseline
)


print("Extreme observation")
print()

print(
    f"Value:              "
    f"{extreme_anomaly.value:.4f} "
    f"{baseline.unit}"
)

print(
    f"Absolute anomaly:   "
    f"{extreme_anomaly.absolute_anomaly:.4f} "
    f"{baseline.unit}"
)

print(
    f"Standardized anomaly:"
    f" {extreme_anomaly.standardized_anomaly:.4f}"
)

print(
    f"Is anomaly:         "
    f"{extreme_anomaly.is_anomaly}"
)

print(
    f"Severity:           "
    f"{extreme_anomaly.severity}"
)

print()


reader.close()

print(
    "Weather Anomaly Detector test complete."
)