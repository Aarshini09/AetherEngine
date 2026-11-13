
import numpy as np

from gnn.data.weather_graph_adapter import WEATHER_FEATURES


class WeatherAnomalyTarget:
    """
    Creates exploratory pseudo-labels from historical weather baselines.

    Baselines are calculated separately for each spatial node and
    selected feature. A node is flagged when any selected feature
    exceeds the configured absolute z-score threshold.

    These are statistical pseudo-labels, not verified extreme-weather
    labels or calibrated probabilities.
    """

    DEFAULT_TARGET_FEATURES = (
        "temperature",
        "mean_sea_level_pressure",
        "total_precipitation",
        "wind_speed",
    )

    def __init__(self, threshold=2.5, target_features=None, epsilon=1e-8):
        if threshold <= 0:
            raise ValueError("threshold must be positive.")

        if epsilon <= 0:
            raise ValueError("epsilon must be positive.")

        self.threshold = float(threshold)
        self.epsilon = float(epsilon)
        self.feature_names = tuple(WEATHER_FEATURES)

        self.target_features = tuple(
            target_features or self.DEFAULT_TARGET_FEATURES
        )

        unknown = set(self.target_features) - set(self.feature_names)
        if unknown:
            raise ValueError(
                f"Unknown target features: {sorted(unknown)}"
            )

        self.feature_indices = np.asarray(
            [self.feature_names.index(name) for name in self.target_features],
            dtype=np.int64,
        )

        self.node_ids = None
        self.mean = None
        self.scale = None
        self.observation_count = 0

    @property
    def is_fitted(self):
        return self.mean is not None and self.scale is not None

    def fit(self, examples):
        """
        Fit per-node baselines from training-period graph examples.

        Each example must contain the adapter's inputs and metadata.
        All graphs must have the same node IDs in the same order.
        """

        total_count = 0
        feature_sum = None
        feature_sum_squares = None

        for example in examples:
            features, node_ids = self._read_example(example)

            selected = features[:, self.feature_indices].astype(np.float64)

            if not np.isfinite(selected).all():
                raise ValueError("Non-finite values found in target features.")

            if self.node_ids is None:
                self.node_ids = tuple(node_ids)
                shape = (len(node_ids), len(self.feature_indices))
                feature_sum = np.zeros(shape, dtype=np.float64)
                feature_sum_squares = np.zeros(shape, dtype=np.float64)
            elif tuple(node_ids) != self.node_ids:
                raise ValueError(
                    "Node IDs or node ordering changed between graphs."
                )

            feature_sum += selected
            feature_sum_squares += np.square(selected)
            total_count += 1

        if total_count == 0:
            raise ValueError("No training graphs were supplied.")

        self.mean = feature_sum / total_count

        variance = feature_sum_squares / total_count - np.square(self.mean)
        variance = np.maximum(variance, 0.0)
        standard_deviation = np.sqrt(variance)

        # Constant features have no useful z-score variation.
        self.scale = np.where(
            standard_deviation < self.epsilon,
            np.inf,
            standard_deviation,
        )

        self.observation_count = total_count
        return self

    def transform(self, example):
        """
        Produce binary pseudo-labels and per-feature anomaly scores.

        Returns:
            labels: float32 array with shape [N, 1]
            details: dictionary with selected feature scores and flags
        """

        self._ensure_fitted()

        features, node_ids = self._read_example(example)

        if tuple(node_ids) != self.node_ids:
            raise ValueError(
                "Graph node IDs/order do not match the fitted baseline."
            )

        selected = features[:, self.feature_indices].astype(np.float64)

        if not np.isfinite(selected).all():
            raise ValueError("Non-finite values found in target features.")

        z_scores = (selected - self.mean) / self.scale
        absolute_scores = np.abs(z_scores)

        feature_flags = absolute_scores >= self.threshold
        labels = np.any(feature_flags, axis=1).astype(np.float32).reshape(-1, 1)

        return labels, {
            "target_feature_names": list(self.target_features),
            "absolute_z_scores": absolute_scores.astype(np.float32),
            "feature_flags": feature_flags,
            "threshold": self.threshold,
            "label_type": "exploratory_statistical_pseudo_label",
        }

    def _read_example(self, example):
        inputs = example["inputs"]
        metadata = example["metadata"]

        if tuple(metadata["feature_names"]) != self.feature_names:
            raise ValueError("Graph feature order does not match WEATHER_FEATURES.")

        features = inputs["node_features"]
        if hasattr(features, "numpy"):
            features = features.numpy()

        features = np.asarray(features)

        if features.ndim != 2 or features.shape[1] != len(self.feature_names):
            raise ValueError("Unexpected node feature tensor shape.")

        node_ids = metadata["node_ids"]

        if len(node_ids) != features.shape[0]:
            raise ValueError("Node ID count does not match feature rows.")

        return features, node_ids

    def _ensure_fitted(self):
        if not self.is_fitted:
            raise RuntimeError("Call fit() before generating anomaly targets.")
