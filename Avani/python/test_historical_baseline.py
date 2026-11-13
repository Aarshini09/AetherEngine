from config import ERA5_RAW_ROOT

from weather.era5_reader import ERA5Reader
from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor
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


print("Historical Temperature Baseline test")
print()

print(
    f"Number of temporal buckets: "
    f"{len(baselines)}"
)

print()


for key in sorted(baselines):

    month, hour = key

    baseline = baselines[key]

    print(
        f"Month: {month:02d}  "
        f"Hour: {hour:02d}  "
        f"Mean: {baseline.mean:.4f} "
        f"{baseline.unit}  "
        f"Std: {baseline.standard_deviation:.4f} "
        f"{baseline.unit}  "
        f"Min: {baseline.minimum:.4f} "
        f"{baseline.unit}  "
        f"Max: {baseline.maximum:.4f} "
        f"{baseline.unit}  "
        f"Samples: {baseline.sample_count}"
    )


print()


test_key = (
    1,
    0
)

baseline = baselines[test_key]

test_value = 20.46376953125

absolute_anomaly = (
    baseline.absolute_anomaly(
        test_value
    )
)

standardized_anomaly = (
    baseline.standardized_anomaly(
        test_value
    )
)


print("January 00:00 baseline test")
print()

print(
    f"Historical mean: "
    f"{baseline.mean:.4f} "
    f"{baseline.unit}"
)

print(
    f"Test value:      "
    f"{test_value:.4f} "
    f"{baseline.unit}"
)

print(
    f"Absolute anomaly:"
    f" {absolute_anomaly:.4f} "
    f"{baseline.unit}"
)

print(
    f"Standardized anomaly:"
    f" {standardized_anomaly:.4f}"
)

print()


reader.close()

print(
    "Historical Temperature Baseline test complete."
)