
from pathlib import Path

import numpy as np

from application.avani_application import AvaniApplication
from gnn.data.era5_dataset_builder import ERA5DatasetBuilder
from gnn.data.weather_anomaly_target import WeatherAnomalyTarget
from gnn.data.weather_feature_normalizer import WeatherFeatureNormalizer
from gnn.data.weather_graph_cache import WeatherGraphCache


WEATHER_DATA_ROOT = r"D:\WeatherData\ERA5\raw"

REGION = {
    "min_latitude": 20.0,
    "max_latitude": 22.0,
    "min_longitude": 78.0,
    "max_longitude": 80.0,
}

# Historical baseline period.
BASELINE_START = "2015-07-01T00:00:00"
BASELINE_END = "2019-06-30T00:00:00"

# Model training period.
TRAIN_START = "2019-07-01T00:00:00"
TRAIN_END = "2019-07-24T00:00:00"

# Held-out evaluation period.
TEST_START = "2019-07-25T00:00:00"
TEST_END = "2019-07-31T00:00:00"

SAMPLE_INTERVAL_HOURS = 24
ANOMALY_THRESHOLD = 2.5

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"


def main():
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    baseline_path = CHECKPOINT_DIR / "era5_anomaly_baseline.npz"
    normalizer_path = CHECKPOINT_DIR / "era5_feature_normalizer.npz"
    train_cache_path = CHECKPOINT_DIR / "era5_train_graphs.npz"
    test_cache_path = CHECKPOINT_DIR / "era5_test_graphs.npz"

    application = AvaniApplication(WEATHER_DATA_ROOT)

    try:
        application.initialize()

        builder = ERA5DatasetBuilder(
            weather_dataset=application.weather_dataset,
            region=REGION,
        )

        print("\n" + "=" * 60)
        print("          AVANI WEATHER DATASET PREPARATION")
        print("=" * 60)

        print("\nRegion:", REGION)
        print("Baseline:", BASELINE_START, "to", BASELINE_END)
        print("Training:", TRAIN_START, "to", TRAIN_END)
        print("Evaluation:", TEST_START, "to", TEST_END)

        # --------------------------------------------------
        # 1. Fit the historical anomaly baseline.
        # --------------------------------------------------
        print("\n[1/6] Fitting historical anomaly baseline...")

        baseline_examples = builder.iter_examples(
            start_time=BASELINE_START,
            end_time=BASELINE_END,
            interval_hours=SAMPLE_INTERVAL_HOURS,
        )

        target_generator = WeatherAnomalyTarget(
            threshold=ANOMALY_THRESHOLD
        )
        target_generator.fit(baseline_examples)

        print(
            "Baseline timestamps:",
            target_generator.observation_count,
        )

        # Persist the fitted target statistics without pickling.
        np.savez_compressed(
            baseline_path,
            mean=target_generator.mean,
            scale=target_generator.scale,
            target_features=np.asarray(
                target_generator.target_features, dtype="U64"
            ),
            threshold=np.asarray([target_generator.threshold]),
            observation_count=np.asarray(
                [target_generator.observation_count]
            ),
        )

        print("Saved baseline:", baseline_path)

        # --------------------------------------------------
        # 2. Generate labeled training graphs.
        # --------------------------------------------------
        print("\n[2/6] Generating training graphs...")

        training_examples = []

        for example in builder.iter_examples(
            start_time=TRAIN_START,
            end_time=TRAIN_END,
            interval_hours=SAMPLE_INTERVAL_HOURS,
        ):
            labels, details = target_generator.transform(example)

            labeled_example = {
                "inputs": example["inputs"],
                "metadata": example["metadata"],
                "labels": labels,
            }
            training_examples.append(labeled_example)

            print(
                f"  {example['metadata']['time']} | "
                f"flagged={int(np.count_nonzero(labels))}"
            )

        if not training_examples:
            raise RuntimeError("No training graphs were generated.")

        # --------------------------------------------------
        # 3. Generate held-out evaluation graphs.
        # --------------------------------------------------
        print("\n[3/6] Generating evaluation graphs...")

        test_examples = []

        for example in builder.iter_examples(
            start_time=TEST_START,
            end_time=TEST_END,
            interval_hours=SAMPLE_INTERVAL_HOURS,
        ):
            labels, details = target_generator.transform(example)

            test_examples.append({
                "inputs": example["inputs"],
                "metadata": example["metadata"],
                "labels": labels,
            })

            print(
                f"  {example['metadata']['time']} | "
                f"flagged={int(np.count_nonzero(labels))}"
            )

        if not test_examples:
            raise RuntimeError("No evaluation graphs were generated.")

        # --------------------------------------------------
        # 4. Fit normalization on training examples only.
        # --------------------------------------------------
        print("\n[4/6] Fitting feature normalizer...")

        normalizer = WeatherFeatureNormalizer()
        normalizer.fit(training_examples)

        normalized_train = [
            {
                **example,
                "inputs": normalizer.transform(example["inputs"]),
            }
            for example in training_examples
        ]

        normalized_test = [
            {
                **example,
                "inputs": normalizer.transform(example["inputs"]),
            }
            for example in test_examples
        ]

        normalizer.save(normalizer_path)
        print("Saved normalizer:", normalizer_path)

        # --------------------------------------------------
        # 5. Save the graph caches.
        # --------------------------------------------------
        print("\n[5/6] Saving graph caches...")

        WeatherGraphCache.save(train_cache_path, normalized_train)
        WeatherGraphCache.save(test_cache_path, normalized_test)

        # --------------------------------------------------
        # 6. Reload and verify both caches.
        # --------------------------------------------------
        print("\n[6/6] Reloading and validating caches...")

        loaded_train = WeatherGraphCache.load(train_cache_path)
        loaded_test = WeatherGraphCache.load(test_cache_path)

        assert len(loaded_train) == len(normalized_train)
        assert len(loaded_test) == len(normalized_test)

        for original, loaded in zip(normalized_train, loaded_train):
            np.testing.assert_allclose(
                original["inputs"]["node_features"],
                loaded["inputs"]["node_features"],
            )
            np.testing.assert_array_equal(
                original["inputs"]["edge_index"],
                loaded["inputs"]["edge_index"],
            )
            np.testing.assert_array_equal(
                original["labels"],
                loaded["labels"],
            )

        for original, loaded in zip(normalized_test, loaded_test):
            np.testing.assert_allclose(
                original["inputs"]["node_features"],
                loaded["inputs"]["node_features"],
            )
            np.testing.assert_array_equal(
                original["labels"],
                loaded["labels"],
            )

        print("\n" + "=" * 60)
        print("          DATASET PREPARATION COMPLETE")
        print("=" * 60)
        print("Training graphs:", len(loaded_train))
        print("Evaluation graphs:", len(loaded_test))
        print("Nodes per graph:", loaded_train[0]["inputs"]["node_features"].shape[0])
        print("Features per node:", loaded_train[0]["inputs"]["node_features"].shape[1])
        print("Training cache:", train_cache_path)
        print("Evaluation cache:", test_cache_path)
        print("Normalizer:", normalizer_path)
        print("Baseline:", baseline_path)

        print(
            "\nReminder: the targets are statistical pseudo-labels, "
            "not verified extreme-weather events."
        )

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
