
from pathlib import Path

import numpy as np

from gnn.data.weather_graph_adapter import WEATHER_FEATURES


class WeatherFeatureNormalizer:
    """
    Standardizes each weather feature independently.

    Fit this only on training examples. Reuse the resulting
    statistics for validation, testing, and inference.

    Each feature is transformed as:

        normalized = (value - mean) / standard_deviation
    """

    def __init__(self, epsilon=1e-8):
        if epsilon <= 0:
            raise ValueError("epsilon must be positive.")

        self.epsilon = float(epsilon)
        self.feature_names = tuple(WEATHER_FEATURES)
        self.mean = None
        self.scale = None
        self.sample_count = 0

    @property
    def is_fitted(self):
        return self.mean is not None and self.scale is not None

    def fit(self, examples):
        """
        Calculate feature statistics from an iterable of graph examples.

        Each example must contain:
            example["inputs"]["node_features"]
            example["metadata"]["feature_names"]

        Accumulates statistics incrementally instead of storing all
        graph tensors in memory.
        """

        feature_count = len(self.feature_names)
        total_count = 0
        feature_sum = np.zeros(feature_count, dtype=np.float64)
        feature_sum_squares = np.zeros(feature_count, dtype=np.float64)

        for example in examples:
            inputs = example["inputs"]
            metadata = example["metadata"]

            names = tuple(metadata["feature_names"])
            if names != self.feature_names:
                raise ValueError(
                    "Feature order mismatch. Expected "
                    f"{self.feature_names}, received {names}."
                )

            features = inputs["node_features"]

            if hasattr(features, "numpy"):
                features = features.numpy()

            features = np.asarray(features, dtype=np.float64)

            if features.ndim != 2:
                raise ValueError(
                    "node_features must have shape [node_count, feature_count]."
                )

            if features.shape[1] != feature_count:
                raise ValueError(
                    f"Expected {feature_count} features per node, "
                    f"received {features.shape[1]}."
                )

            if features.shape[0] == 0:
                continue

            if not np.isfinite(features).all():
                raise ValueError(
                    "Non-finite feature values detected. "
                    "Handle missing values before fitting normalization."
                )

            total_count += features.shape[0]
            feature_sum += features.sum(axis=0)
            feature_sum_squares += np.square(features).sum(axis=0)

        if total_count == 0:
            raise ValueError(
                "Cannot fit the normalizer: no valid graph nodes were supplied."
            )

        mean = feature_sum / total_count
        variance = feature_sum_squares / total_count - np.square(mean)

        # Floating-point round-off can produce tiny negative variances.
        variance = np.maximum(variance, 0.0)
        standard_deviation = np.sqrt(variance)

        # Constant features are centered but not divided by zero.
        scale = np.where(
            standard_deviation < self.epsilon,
            1.0,
            standard_deviation,
        )

        self.mean = mean
        self.scale = scale
        self.sample_count = total_count

        return self

    def transform(self, inputs, feature_names=None):
        """Return a copy of model inputs with normalized node features."""

        self._ensure_fitted()

        if feature_names is not None:
            if tuple(feature_names) != self.feature_names:
                raise ValueError("Feature order does not match the fitted normalizer.")

        features = inputs["node_features"]

        if hasattr(features, "numpy"):
            features = features.numpy()

        features = np.asarray(features, dtype=np.float32)

        if features.ndim != 2 or features.shape[1] != len(self.feature_names):
            raise ValueError(
                "node_features has an unexpected shape."
            )

        if not np.isfinite(features).all():
            raise ValueError(
                "Non-finite values found before normalization."
            )

        normalized = (features - self.mean) / self.scale

        result = dict(inputs)
        result["node_features"] = normalized.astype(np.float32)

        return result

    def fit_transform(self, examples):
        """
        Fit from examples and return normalized copies.

        This convenience method materializes its outputs in memory.
        Prefer fit() followed by transform() for large datasets.
        """

        examples = list(examples)
        self.fit(examples)

        return [
            {
                **example,
                "inputs": self.transform(
                    example["inputs"],
                    example["metadata"]["feature_names"],
                ),
            }
            for example in examples
        ]

    def save(self, path):
        """Save normalization statistics and feature order to an NPZ file."""

        self._ensure_fitted()

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        np.savez(
            path,
            mean=self.mean,
            scale=self.scale,
            feature_names=np.asarray(self.feature_names, dtype=str),
            sample_count=np.asarray(self.sample_count, dtype=np.int64),
            epsilon=np.asarray(self.epsilon, dtype=np.float64),
        )

    @classmethod
    def load(cls, path):
        """Load saved normalization statistics."""

        with np.load(path, allow_pickle=False) as data:
            feature_names = tuple(data["feature_names"].tolist())

            if feature_names != tuple(WEATHER_FEATURES):
                raise ValueError(
                    "Saved feature order does not match WEATHER_FEATURES."
                )

            normalizer = cls(epsilon=float(data["epsilon"]))
            normalizer.mean = data["mean"].astype(np.float64)
            normalizer.scale = data["scale"].astype(np.float64)
            normalizer.sample_count = int(data["sample_count"])

        if (
            normalizer.mean.shape != (len(WEATHER_FEATURES),)
            or normalizer.scale.shape != (len(WEATHER_FEATURES),)
            or not np.isfinite(normalizer.mean).all()
            or not np.isfinite(normalizer.scale).all()
            or np.any(normalizer.scale <= 0)
        ):
            raise ValueError("Saved normalization statistics are invalid.")

        return normalizer

    def _ensure_fitted(self):
        if not self.is_fitted:
            raise RuntimeError(
                "Normalizer has not been fitted. Call fit() first."
            )
