
import tensorflow as tf


class GraphMessagePassing(tf.keras.layers.Layer):
    """
    Updates each node using information from its connected neighbours.

    edge_index[0] contains source-node indices.
    edge_index[1] contains destination-node indices.
    """

    def __init__(self, hidden_dim: int, **kwargs):
        super().__init__(**kwargs)

        self.hidden_dim = hidden_dim

        self.message_network = tf.keras.Sequential([
            tf.keras.layers.Dense(hidden_dim, activation="relu"),
            tf.keras.layers.Dense(hidden_dim),
        ])

        self.update_network = tf.keras.Sequential([
            tf.keras.layers.Dense(hidden_dim, activation="relu"),
            tf.keras.layers.Dense(hidden_dim),
        ])

    def call(self, node_states, edge_index):
        source_indices = tf.cast(edge_index[0], tf.int32)
        target_indices = tf.cast(edge_index[1], tf.int32)

        source_states = tf.gather(node_states, source_indices)
        target_states = tf.gather(node_states, target_indices)

        # Each edge produces a message from source to destination.
        edge_features = tf.concat(
            [source_states, target_states], axis=-1
        )

        messages = self.message_network(edge_features)

        # Aggregate incoming messages at each destination node.
        node_count = tf.shape(node_states)[0]

        aggregated = tf.math.unsorted_segment_mean(
            messages,
            target_indices,
            node_count,
        )

        # Isolated nodes receive a zero aggregated message.
        aggregated = tf.where(
            tf.math.is_finite(aggregated),
            aggregated,
            tf.zeros_like(aggregated),
        )

        updated_states = self.update_network(
            tf.concat([node_states, aggregated], axis=-1)
        )

        # Residual connection preserves the existing representation.
        return node_states + updated_states


class WeatherGNN(tf.keras.Model):
    """
    Initial spatial GNN for weather-cell analysis.

    Inputs:
        node_features: [number_of_nodes, input_features]
        edge_index:    [2, number_of_edges]

    Output:
        anomaly_scores: [number_of_nodes, 1]

    This is an untrained model until suitable data and targets
    are provided and training is performed.
    """

    def __init__(
        self,
        input_features: int = 10,
        hidden_dim: int = 64,
        message_passing_layers: int = 2,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if input_features < 1:
            raise ValueError("input_features must be positive.")

        if hidden_dim < 1:
            raise ValueError("hidden_dim must be positive.")

        if message_passing_layers < 1:
            raise ValueError(
                "message_passing_layers must be at least 1."
            )

        self.input_features = input_features
        self.hidden_dim = hidden_dim
        self.message_passing_layers = message_passing_layers

        self.encoder = tf.keras.layers.Dense(
            hidden_dim,
            activation="relu",
            name="node_encoder",
        )

        self.graph_layers = [
            GraphMessagePassing(
                hidden_dim,
                name=f"message_passing_{index + 1}",
            )
            for index in range(message_passing_layers)
        ]

        self.anomaly_head = tf.keras.layers.Dense(
            1,
            activation="sigmoid",
            name="anomaly_score",
        )

    def call(self, inputs, training=False):
        node_features = tf.cast(
            inputs["node_features"], tf.float32
        )
        edge_index = tf.cast(inputs["edge_index"], tf.int32)

        tf.debugging.assert_rank(node_features, 2)
        tf.debugging.assert_equal(
            tf.shape(node_features)[1],
            self.input_features,
            message="Unexpected number of node features.",
        )
        tf.debugging.assert_rank(edge_index, 2)
        tf.debugging.assert_equal(
            tf.shape(edge_index)[0],
            2,
            message="edge_index must have shape [2, E].",
        )
        tf.debugging.assert_greater_equal(edge_index, 0)
        tf.debugging.assert_less(
            edge_index,
            tf.shape(node_features)[0],
            message="An edge refers to a nonexistent node.",
        )

        states = self.encoder(node_features)

        for graph_layer in self.graph_layers:
            states = graph_layer(states, edge_index)

        return self.anomaly_head(states)

    def get_config(self):
        config = super().get_config()
        config.update({
            "input_features": self.input_features,
            "hidden_dim": self.hidden_dim,
            "message_passing_layers": self.message_passing_layers,
        })
        return config
