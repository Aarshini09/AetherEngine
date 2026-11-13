
from application.avani_application import AvaniApplication

from gnn.data.era5_dataset_builder import ERA5DatasetBuilder
from gnn.data.weather_feature_normalizer import WeatherFeatureNormalizer


WEATHER_DATA_ROOT = r"D:\WeatherData\ERA5\raw"

REGION = {
    "min_latitude": 20.0,
    "max_latitude": 22.0,
    "min_longitude": 78.0,
    "max_longitude": 80.0,
}

TRAIN_START = "2019-07-15T00:00:00"
TRAIN_END = "2019-07-15T18:00:00"

TEST_START = "2019-07-16T00:00:00"
TEST_END = "2019-07-16T00:00:00"

NORMALIZER_PATH = "gnn/checkpoints/era5_feature_normalizer.npz"


def main():
    application = AvaniApplication(WEATHER_DATA_ROOT)

    try:
        application.initialize()

        builder = ERA5DatasetBuilder(
            weather_dataset=application.weather_dataset,
            region=REGION,
        )

        # Four timestamps for fitting; the following timestamp is held out.
        training_examples = list(
            builder.iter_examples(
                start_time=TRAIN_START,
                end_time=TRAIN_END,
                interval_hours=6,
            )
        )

        print("Training graphs:", len(training_examples))

        normalizer = WeatherFeatureNormalizer()
        normalizer.fit(training_examples)

        print("Training node observations:", normalizer.sample_count)
        print("Feature means:", normalizer.mean)
        print("Feature scales:", normalizer.scale)

        # Fit only on training data. Never refit on the held-out example.
        normalizer.save(NORMALIZER_PATH)
        restored = WeatherFeatureNormalizer.load(NORMALIZER_PATH)

        test_examples = list(
            builder.iter_examples(
                start_time=TEST_START,
                end_time=TEST_END,
                interval_hours=6,
            )
        )

        if len(test_examples) != 1:
            raise RuntimeError(
                f"Expected one test graph, received {len(test_examples)}."
            )

        test_example = test_examples[0]

        normalized_inputs = restored.transform(
            test_example["inputs"],
            test_example["metadata"]["feature_names"],
        )

        normalized_features = normalized_inputs["node_features"]

        print("Held-out timestamp:", test_example["metadata"]["time"])
        print("Normalized shape:", normalized_features.shape)
        print("All normalized values finite:", bool(
            __import__("numpy").isfinite(normalized_features).all()
        ))
        print("First normalized node:", normalized_features[0])

        assert normalized_features.shape == (81, 8)
        assert restored.sample_count == 81 * 4

        print("\nWeather feature normalization test passed.")

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
