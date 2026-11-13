from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import (
    WeatherDataBridge
)

from weather.weather_dataset import (
    WeatherDataset
)

from weather.weather_grid_index import (
    WeatherGridIndex
)

from weather.weather_data_index import (
    WeatherDataIndex
)

from weather.era5_reader import (
    ERA5Reader
)

from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor
)

from weather.anomaly_detector import (
    AnomalyDetector
)

from weather.anomaly_classifier import (
    AnomalyClassifier
)

from weather.anomaly_field_builder import (
    AnomalyFieldBuilder
)

from weather.anomaly_region_builder import (
    AnomalyRegionBuilder
)


# ---------------------------------------------------------
# Weather dataset
# ---------------------------------------------------------

bridge = WeatherDataBridge(
    ERA5_RAW_ROOT
)

dataset = WeatherDataset(
    bridge
)

dataset.open()


# ---------------------------------------------------------
# Spatial index
# ---------------------------------------------------------

grid_index = WeatherGridIndex(
    bridge.get_reader(
        "temperature"
    )
)

grid_index.initialize()


data_index = WeatherDataIndex(
    grid_index
)

data_index.build(
    min_latitude=20.0,
    max_latitude=21.0,
    min_longitude=78.0,
    max_longitude=80.0
)


# ---------------------------------------------------------
# Historical baseline
# ---------------------------------------------------------

temperature_file = (
    ERA5_RAW_ROOT
    / "temperature_2015_2019.nc"
)

reader = ERA5Reader(
    temperature_file
)

reader.open()


baseline_processor = (
    HistoricalBaselineProcessor(
        reader
    )
)


baselines = (
    baseline_processor.compute_point_baseline(
        variable_name="temperature",

        latitude=20.5937,
        longitude=78.9629,

        start_time="2015-01-01T00:00:00",
        end_time="2019-12-31T18:00:00"
    )
)


# ---------------------------------------------------------
# Anomaly system
# ---------------------------------------------------------

detector = AnomalyDetector(
    threshold=2.0
)

classifier = AnomalyClassifier()


field_builder = AnomalyFieldBuilder(
    weather_dataset=dataset,

    data_index=data_index,

    baseline_processor=baseline_processor,

    anomaly_detector=detector,

    anomaly_classifier=classifier
)


# ---------------------------------------------------------
# Build anomaly field
# ---------------------------------------------------------

time = "2015-01-01T00:00:00"


field = field_builder.build(
    variable="temperature",

    time=time,

    baselines=baselines
)


# ---------------------------------------------------------
# Build anomaly regions
# ---------------------------------------------------------

region_builder = AnomalyRegionBuilder(
    data_index
)


regions = region_builder.build(
    field
)


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("Weather Anomaly Region test")
print()

print(
    f"Spatial nodes:       "
    f"{data_index.get_node_count()}"
)

print(
    f"Anomalous nodes:     "
    f"{field.get_anomaly_count()}"
)

print(
    f"Anomaly regions:     "
    f"{len(regions)}"
)

print()


for region in regions:

    print(
        f"Region {region.region_id}"
    )

    print(
        f"  Category:       "
        f"{region.category}"
    )

    print(
        f"  Node count:     "
        f"{region.node_count}"
    )

    print(
        f"  Nodes:          "
        f"{sorted(region.node_ids)}"
    )

    print(
        f"  Latitude range: "
        f"{region.min_latitude} "
        f"→ "
        f"{region.max_latitude}"
    )

    print(
        f"  Longitude range:"
        f" {region.min_longitude} "
        f"→ "
        f"{region.max_longitude}"
    )

    print(
        f"  Latitude span:  "
        f"{region.latitude_span}"
    )

    print(
        f"  Longitude span: "
        f"{region.longitude_span}"
    )

    print(
        f"  Value range:    "
        f"{region.min_value:.4f} "
        f"→ "
        f"{region.max_value:.4f} °C"
    )

    print(
        f"  Z-score range:  "
        f"{region.min_standardized_anomaly:.4f} "
        f"→ "
        f"{region.max_standardized_anomaly:.4f}"
    )

    print()


reader.close()

dataset.close()

print(
    "Weather Anomaly Region test complete."
)