
import tensorflow as tf

from models.weather_gnn import WeatherGNN


def main():
    tf.random.set_seed(42)

    # Four example nodes, each with ten features.
    node_features = tf.random.normal((4, 10))

    # Edges describe which nodes send information to which
    # neighbouring nodes. These are illustrative connections.
    edge_index = tf.constant([
        [0, 1, 1, 2, 2, 3, 3, 0],
        [1, 0, 2, 1, 3, 2, 0, 3],
    ], dtype=tf.int32)

    model = WeatherGNN(
        input_features=10,
        hidden_dim=64,
        message_passing_layers=2,
    )

    predictions = model({
        "node_features": node_features,
        "edge_index": edge_index,
    })

    print("TensorFlow:", tf.__version__)
    print("Input node shape:", node_features.shape)
    print("Edge index shape:", edge_index.shape)
    print("Prediction shape:", predictions.shape)
    print("Trainable parameters:", model.count_params())
    print("\nInitial anomaly scores:")
    print(predictions.numpy())


if __name__ == "__main__":
    main()
