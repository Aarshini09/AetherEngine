
from application.avani_application import AvaniApplication

from gnn.data.era5_dataset_builder import ERA5DatasetBuilder


WEATHER_DATA_ROOT = r"D:\WeatherData\ERA5\raw"

REGION = {
    "min_latitude": 20.0,
    "max_latitude": 22.0,
    "min_longitude": 78.0,
    "max_longitude": 80.0,
}

START_TIME = "2019-07-15T00:00:00"
END_TIME = "2019-07-16T00:00:00"


def main():
    application = AvaniApplication(WEATHER_DATA_ROOT)

    try:
        application.initialize()

        builder = ERA5DatasetBuilder(
            weather_dataset=application.weather_dataset,
            region=REGION,
        )

        print("Spatial nodes:", builder.node_count)

        example_count = 0

        for example in builder.iter_examples(
            start_time=START_TIME,
            end_time=END_TIME,
            interval_hours=6,
        ):
            inputs = example["inputs"]
            metadata = example["metadata"]

            print("\nTimestamp:", metadata["time"])
            print("Node features:", inputs["node_features"].shape)
            print("Edge index:", inputs["edge_index"].shape)
            print("Feature names:", metadata["feature_names"])

            example_count += 1

        print("\nDataset builder test passed.")
        print("Graph examples produced:", example_count)

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
