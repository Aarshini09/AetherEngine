
import numpy as np

from application.avani_application import AvaniApplication
from gnn.data.era5_dataset_builder import ERA5DatasetBuilder
from gnn.data.weather_anomaly_target import WeatherAnomalyTarget


WEATHER_DATA_ROOT = r"D:\WeatherData\ERA5\raw"

REGION = {
    "min_latitude": 20.0,
    "max_latitude": 22.0,
    "min_longitude": 78.0,
    "max_longitude": 80.0,
}

# Historical baseline: July 2015 through June 2019.
TRAIN_START = "2015-07-01T00:00:00"
TRAIN_END = "2019-06-30T00:00:00"

# Evaluation period: July 2019.
TEST_START = "2019-07-01T00:00:00"
TEST_END = "2019-07-31T00:00:00"

SAMPLE_INTERVAL_HOURS = 24
ANOMALY_THRESHOLD = 2.5


def main():
    application = AvaniApplication(WEATHER_DATA_ROOT)

    try:
        application.initialize()

        builder = ERA5DatasetBuilder(
            weather_dataset=application.weather_dataset,
            region=REGION,
        )

        print("\n" + "=" * 55)
        print("       HISTORICAL WEATHER ANOMALY BASELINE")
        print("=" * 55)

        print("\nInitializing regional weather graph...")
        print("Region:", REGION)
        print("Sampling interval:", SAMPLE_INTERVAL_HOURS, "hours")
        print("Training period:", TRAIN_START, "to", TRAIN_END)
        print("Evaluation period:", TEST_START, "to", TEST_END)

        # Fit directly from the generator to avoid storing every graph.
        training_examples = builder.iter_examples(
            start_time=TRAIN_START,
            end_time=TRAIN_END,
            interval_hours=SAMPLE_INTERVAL_HOURS,
        )

        target_generator = WeatherAnomalyTarget(
            threshold=ANOMALY_THRESHOLD
        )

        print("\nFitting historical baseline...")
        target_generator.fit(training_examples)

        print("\nBaseline fitted successfully.")
        print(
            "Historical timestamps used:",
            target_generator.observation_count,
        )
        print("Target features:", target_generator.target_features)
        print("Threshold:", ANOMALY_THRESHOLD)

        # Evaluation timestamps are not used to fit the baseline.
        evaluation_examples = builder.iter_examples(
            start_time=TEST_START,
            end_time=TEST_END,
            interval_hours=SAMPLE_INTERVAL_HOURS,
        )

        total_graphs = 0
        total_nodes = 0
        total_flagged_nodes = 0
        maximum_absolute_z = 0.0
        z_score_sum = 0.0
        z_score_count = 0

        feature_flag_counts = {
            feature: 0
            for feature in target_generator.target_features
        }

        print("\nEvaluating held-out July 2019 data...")

        for example in evaluation_examples:
            labels, details = target_generator.transform(example)

            labels = np.asarray(labels, dtype=np.float32)
            absolute_z = np.asarray(
                details["absolute_z_scores"],
                dtype=np.float64,
            )
            feature_flags = np.asarray(details["feature_flags"])

            if labels.ndim != 2 or labels.shape[1] != 1:
                raise ValueError(
                    f"Unexpected label shape: {labels.shape}"
                )

            if not np.all(np.isfinite(labels)):
                raise ValueError("Generated labels contain non-finite values.")

            if not np.all(np.isin(labels, [0.0, 1.0])):
                raise ValueError("Generated labels are not binary.")

            total_graphs += 1
            node_count = labels.shape[0]
            total_nodes += node_count

            flagged_nodes = int(np.count_nonzero(labels))
            total_flagged_nodes += flagged_nodes

            if absolute_z.size:
                maximum_absolute_z = max(
                    maximum_absolute_z,
                    float(np.max(absolute_z)),
                )
                z_score_sum += float(np.sum(absolute_z))
                z_score_count += int(absolute_z.size)

            feature_names = details.get(
                "target_feature_names",
                target_generator.target_features,
            )

            if feature_flags.ndim == 2:
                for index, feature in enumerate(feature_names):
                    if index < feature_flags.shape[1]:
                        feature_flag_counts[feature] += int(
                            np.count_nonzero(feature_flags[:, index])
                        )

            timestamp = example["metadata"]["time"]

            print(
                f"{timestamp} | "
                f"nodes={node_count} | "
                f"flagged={flagged_nodes} | "
                f"max_abs_z="
                f"{float(np.max(absolute_z)) if absolute_z.size else 0.0:.3f}"
            )

        if total_graphs == 0:
            raise RuntimeError(
                "No evaluation graphs were generated. "
                "Check the ERA5 timestamps and selected region."
            )

        print("\n" + "=" * 55)
        print("                 RESULTS")
        print("=" * 55)

        print("Evaluation graphs:", total_graphs)
        print("Total node observations:", total_nodes)
        print("Total flagged node observations:", total_flagged_nodes)

        flagged_percentage = (
            100.0 * total_flagged_nodes / total_nodes
            if total_nodes
            else 0.0
        )

        print(f"Flagged node percentage: {flagged_percentage:.2f}%")
        print(f"Maximum absolute z-score: {maximum_absolute_z:.4f}")

        if z_score_count:
            print(
                "Mean absolute z-score:",
                f"{z_score_sum / z_score_count:.4f}",
            )

        print("\nFlagged observations by feature:")
        for feature, count in feature_flag_counts.items():
            print(f"  {feature}: {count}")

        print("\nHistorical anomaly-target test passed.")
        print(
            "These are statistical pseudo-labels, not verified "
            "extreme-weather events."
        )

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
