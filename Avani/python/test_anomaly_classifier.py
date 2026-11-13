from config import ERA5_RAW_ROOT

from weather.era5_reader import ERA5Reader
from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor
)
from weather.anomaly_detector import AnomalyDetector
from weather.anomaly_classifier import (
    AnomalyClassifier
)


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

classifier = AnomalyClassifier()


print("Weather Anomaly Classification test")
print()


# ---------------------------------------------------------
# Positive temperature anomaly
# ---------------------------------------------------------

hot_value = (
    baseline.mean
    + (
        baseline.standard_deviation
        * 4.5
    )
)


hot_anomaly = detector.detect(
    variable="temperature",

    time="2015-01-01T00:00:00",

    latitude=20.5937,
    longitude=78.9629,

    value=hot_value,

    baseline=baseline
)


hot_classification = classifier.classify(
    hot_anomaly
)


print("Positive temperature anomaly")
print()

print(
    f"Value:              "
    f"{hot_anomaly.value:.4f} "
    f"{baseline.unit}"
)

print(
    f"Z-score:            "
    f"{hot_anomaly.standardized_anomaly:.4f}"
)

print(
    f"Anomaly:            "
    f"{hot_anomaly.is_anomaly}"
)

print(
    f"Category:           "
    f"{hot_classification.category}"
)

print(
    f"Direction:          "
    f"{hot_classification.direction}"
)

print(
    f"Severity:            "
    f"{hot_classification.severity}"
)

print(
    f"Extreme:             "
    f"{hot_classification.is_extreme}"
)

print()


# ---------------------------------------------------------
# Negative temperature anomaly
# ---------------------------------------------------------

cold_value = (
    baseline.mean
    - (
        baseline.standard_deviation
        * 4.5
    )
)


cold_anomaly = detector.detect(
    variable="temperature",

    time="2015-01-01T00:00:00",

    latitude=20.5937,
    longitude=78.9629,

    value=cold_value,

    baseline=baseline
)


cold_classification = classifier.classify(
    cold_anomaly
)


print("Negative temperature anomaly")
print()

print(
    f"Value:              "
    f"{cold_anomaly.value:.4f} "
    f"{baseline.unit}"
)

print(
    f"Z-score:            "
    f"{cold_anomaly.standardized_anomaly:.4f}"
)

print(
    f"Anomaly:            "
    f"{cold_anomaly.is_anomaly}"
)

print(
    f"Category:           "
    f"{cold_classification.category}"
)

print(
    f"Direction:          "
    f"{cold_classification.direction}"
)

print(
    f"Severity:            "
    f"{cold_classification.severity}"
)

print(
    f"Extreme:             "
    f"{cold_classification.is_extreme}"
)

print()


reader.close()

print(
    "Weather Anomaly Classification test complete."
)