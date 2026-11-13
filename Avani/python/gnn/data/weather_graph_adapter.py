
from datetime import datetime
import math

import numpy as np
import tensorflow as tf


WEATHER_FEATURES = (
    "temperature",
    "dewpoint",
    "mean_sea_level_pressure",
    "surface_pressure",
    "wind_u",
    "wind_v",
    "total_precipitation",
    "wind_speed",
)

FEATURE_COUNT = len(WEATHER_FEATURES)


class WeatherGraphAdapter:
    """
    Converts an Avani WeatherDataGraph at one timestamp
    into tensors accepted by WeatherGNN.

    Spatial topology comes from WeatherDataIndex neighbors.
    Weather features come from WeatherState objects.
    """

    @staticmethod
    def convert(graph, time):
        if not graph.node_series:
            raise ValueError(
                "WeatherDataGraph is empty. Build it before conversion."
            )

        # Preserve the graph's stable node-ID ordering.
        node_ids = list(graph.data_index.nodes.keys())

        node_to_index = {
            node_id: index
            for index, node_id in enumerate(node_ids)
        }

        feature_rows = []

        for node_id in node_ids:
            state = graph.get_state(node_id, time)

            if state is None:
                raise ValueError(
                    f"Missing weather state for node {node_id} "
                    f"at time {time!r}."
                )

            values = [
                getattr(state, feature_name)
                for feature_name in WEATHER_FEATURES
            ]

            try:
                values = [float(value) for value in values]
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Non-numeric weather feature at node {node_id}."
                ) from exc

            if not all(math.isfinite(value) for value in values):
                raise ValueError(
                    f"Non-finite weather feature at node {node_id}, "
                    f"time {time!r}. Missing-value handling is required "
                    "before converting this graph."
                )

            feature_rows.append(values)

        # Directed source -> target edges.
        # Add each neighbor relationship as an edge.
        sources = []
        targets = []

        for node_id in node_ids:
            source_index = node_to_index[node_id]

            for neighbor_id in graph.get_spatial_neighbor_ids(node_id):
                if neighbor_id not in node_to_index:
                    continue

                target_index = node_to_index[neighbor_id]

                sources.append(source_index)
                targets.append(target_index)

        node_features = tf.convert_to_tensor(
            np.asarray(feature_rows, dtype=np.float32),
            dtype=tf.float32,
        )

        edge_index = tf.convert_to_tensor(
            np.asarray([sources, targets], dtype=np.int32).reshape(2, -1),
            dtype=tf.int32,
        )

        return {
            "node_features": node_features,
            "edge_index": edge_index,
        }, {
            "node_ids": node_ids,
            "node_to_index": node_to_index,
            "time": time,
            "feature_names": list(WEATHER_FEATURES),
        }
