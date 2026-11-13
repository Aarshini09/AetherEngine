
from pathlib import Path
import json

import numpy as np


class WeatherGraphCache:
    """Persist graph features, edges, labels, and metadata safely."""

    FORMAT_VERSION = 1

    @staticmethod
    def save(path, examples):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        examples = list(examples)
        if not examples:
            raise ValueError("Cannot cache an empty dataset.")

        features = []
        edges = []
        labels = []
        timestamps = []
        node_ids = []
        feature_names = []

        for example in examples:
            inputs = example["inputs"]
            metadata = example["metadata"]

            x = np.asarray(inputs["node_features"], dtype=np.float32)
            edge_index = np.asarray(inputs["edge_index"], dtype=np.int64)

            if x.ndim != 2:
                raise ValueError("node_features must have shape [N, F].")

            if edge_index.ndim != 2 or edge_index.shape[0] != 2:
                raise ValueError("edge_index must have shape [2, E].")

            ids = list(metadata["node_ids"])
            names = list(metadata["feature_names"])

            if len(ids) != x.shape[0]:
                raise ValueError("Node ID count does not match node features.")

            if len(names) != x.shape[1]:
                raise ValueError("Feature names do not match feature columns.")

            if edge_index.size and (
                edge_index.min() < 0 or edge_index.max() >= x.shape[0]
            ):
                raise ValueError("Graph contains an invalid edge index.")

            if not np.all(np.isfinite(x)):
                raise ValueError("Node features contain non-finite values.")

            y = example.get("labels")
            if y is None:
                y = np.zeros((x.shape[0], 1), dtype=np.float32)
                has_labels = False
            else:
                y = np.asarray(y, dtype=np.float32)
                has_labels = True

            if y.shape != (x.shape[0], 1):
                raise ValueError("Labels must have shape [N, 1].")

            features.append(x)
            edges.append(edge_index)
            labels.append(y)
            timestamps.append(str(metadata["time"]))
            node_ids.append([str(node_id) for node_id in ids])
            feature_names.append(names)

        # This cache format supports fixed regional graph geometry.
        reference_ids = node_ids[0]
        reference_names = feature_names[0]

        for i in range(len(examples)):
            if node_ids[i] != reference_ids:
                raise ValueError("Node IDs/order differ between graph examples.")
            if feature_names[i] != reference_names:
                raise ValueError("Feature order differs between graph examples.")
            if features[i].shape != features[0].shape:
                raise ValueError("Node feature shapes differ between examples.")
            if edges[i].shape != edges[0].shape or not np.array_equal(
                edges[i], edges[0]
            ):
                raise ValueError("Graph topology differs between examples.")

        if not all("labels" in item for item in examples):
            raise ValueError(
                "Every example must have labels before saving the training cache."
            )

        np.savez_compressed(
            path,
            format_version=np.array([WeatherGraphCache.FORMAT_VERSION]),
            node_features=np.stack(features),
            edge_index=edges[0],
            labels=np.stack(labels),
            timestamps=np.asarray(timestamps, dtype="U32"),
            node_ids=np.asarray(reference_ids, dtype="U64"),
            feature_names=np.asarray(reference_names, dtype="U64"),
            metadata_json=np.asarray(
                json.dumps({
                    "example_count": len(examples),
                    "node_count": int(features[0].shape[0]),
                    "feature_count": int(features[0].shape[1]),
                    "edge_count": int(edges[0].shape[1]),
                })
            ),
        )

        print(f"[Graph Cache] Saved {len(examples)} examples to {path}")

    @staticmethod
    def load(path):
        path = Path(path)

        if not path.is_file():
            raise FileNotFoundError(f"Graph cache not found: {path}")

        with np.load(path, allow_pickle=False) as archive:
            version = int(archive["format_version"][0])
            if version != WeatherGraphCache.FORMAT_VERSION:
                raise ValueError(f"Unsupported graph cache version: {version}")

            features = archive["node_features"].copy()
            edges = archive["edge_index"].copy()
            labels = archive["labels"].copy()
            timestamps = archive["timestamps"].astype(str).tolist()
            node_ids = archive["node_ids"].astype(str).tolist()
            feature_names = archive["feature_names"].astype(str).tolist()
            metadata = json.loads(str(archive["metadata_json"].item()))

        if features.ndim != 3:
            raise ValueError("Cached node_features must have shape [T, N, F].")

        if labels.shape != (*features.shape[:2], 1):
            raise ValueError("Cached labels do not match feature dimensions.")

        if edges.ndim != 2 or edges.shape[0] != 2:
            raise ValueError("Cached edge_index must have shape [2, E].")

        if len(timestamps) != features.shape[0]:
            raise ValueError("Timestamp count does not match cached examples.")

        if len(node_ids) != features.shape[1]:
            raise ValueError("Node ID count does not match cached nodes.")

        if len(feature_names) != features.shape[2]:
            raise ValueError("Feature names do not match cached features.")

        if not np.all(np.isfinite(features)):
            raise ValueError("Cached features contain non-finite values.")

        examples = []

        for i, timestamp in enumerate(timestamps):
            examples.append({
                "inputs": {
                    "node_features": features[i].copy(),
                    "edge_index": edges.copy(),
                },
                "labels": labels[i].copy(),
                "metadata": {
                    "time": timestamp,
                    "node_ids": node_ids.copy(),
                    "feature_names": feature_names.copy(),
                },
            })

        print(f"[Graph Cache] Loaded {len(examples)} examples from {path}")
        print(f"[Graph Cache] Metadata: {metadata}")

        return examples
