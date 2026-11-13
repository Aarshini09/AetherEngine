from config import ERA5_RAW_ROOT

from weather.era5_reader import ERA5Reader
from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_grid_index import WeatherGridIndex
from weather.weather_data_index import WeatherDataIndex

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


temperature_file = (
    ERA5_RAW_ROOT
    / "temperature_2015_2019.nc"
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


builder = AnomalyFieldBuilder(
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


field = builder.build(
    variable="temperature",

    time=time,

    baselines=baselines
)


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("Weather Anomaly Field test")
print()

print(
    f"Spatial nodes:       "
    f"{data_index.get_node_count()}"
)

print(
    f"Anomalous nodes:     "
    f"{field.get_anomaly_count()}"
)

print()

print(
    "Anomaly categories:"
)

category_counts = (
    field.get_node_count_by_category()
)

for category, count in (
    category_counts.items()
):

    print(
        f"  {category}: {count}"
    )

print()

print(
    "Anomalous nodes:"
)

for node_id in (
    field.get_anomalous_node_ids()
):

    node = data_index.get_node(
        node_id
    )

    anomaly = field.get_anomaly(
        node_id
    )

    classification = (
        field.get_classification(
            node_id
        )
    )

    print(
        f"  Node {node_id}: "
        f"{node.coordinate.latitude}, "
        f"{node.coordinate.longitude} | "
        f"{anomaly.value:.2f} °C | "
        f"z={anomaly.standardized_anomaly:.2f} | "
        f"{classification.category}"
    )


print()

reader.close()

dataset.close()

print(
    "Weather Anomaly Field test complete."
)