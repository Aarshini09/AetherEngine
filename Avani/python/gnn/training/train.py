
from pathlib import Path

import tensorflow as tf

from models.weather_gnn import WeatherGNN


SEED = 42
INPUT_FEATURES = 10
HIDDEN_DIM = 64
MESSAGE_PASSING_LAYERS = 2

TRAINING_GRAPHS = 160
VALIDATION_GRAPHS = 40
NODES_PER_GRAPH = 32
EPOCHS = 30
LEARNING_RATE = 1e-3

CHECKPOINT_DIR = Path(__file__).resolve().parents[1] / "checkpoints"
CHECKPOINT_PATH = CHECKPOINT_DIR / "weather_gnn.weights.h5"


def make_graph(seed: int):
    """Create a reproducible ring graph and synthetic binary labels."""
    generator = tf.random.Generator.from_seed(seed)

    features = generator.normal(
        shape=(NODES_PER_GRAPH, INPUT_FEATURES),
        dtype=tf.float32,
    )

    # Bidirectional ring: each node connects to its two neighbours.
    nodes = tf.range(NODES_PER_GRAPH, dtype=tf.int32)
    next_nodes = (nodes + 1) % NODES_PER_GRAPH

    edge_sources = tf.concat([nodes, next_nodes], axis=0)
    edge_targets = tf.concat([next_nodes, nodes], axis=0)

    edge_index = tf.stack([edge_sources, edge_targets], axis=0)

    # Synthetic target rule, not a real weather label.
    labels = tf.cast(features[:, 0] > 0.0, tf.float32)
    labels = labels[:, tf.newaxis]

    return {
        "node_features": features,
        "edge_index": edge_index,
    }, labels


def make_dataset(start_seed: int, count: int):
    return [
        make_graph(start_seed + index)
        for index in range(count)
    ]


def evaluate(model, dataset, loss_function):
    total_loss = 0.0
    correct = 0
    total = 0

    for graph, labels in dataset:
        predictions = model(graph, training=False)

        loss = loss_function(labels, predictions)
        total_loss += float(loss.numpy())

        predicted_classes = predictions >= 0.5
        actual_classes = labels >= 0.5

        correct += int(
            tf.reduce_sum(
                tf.cast(
                    predicted_classes == actual_classes,
                    tf.int32,
                )
            ).numpy()
        )
        total += int(tf.size(labels).numpy())

    return total_loss / len(dataset), correct / total


def main():
    tf.keras.utils.set_random_seed(SEED)

    training_data = make_dataset(1000, TRAINING_GRAPHS)
    validation_data = make_dataset(
        10000,
        VALIDATION_GRAPHS,
    )

    model = WeatherGNN(
        input_features=INPUT_FEATURES,
        hidden_dim=HIDDEN_DIM,
        message_passing_layers=MESSAGE_PASSING_LAYERS,
    )

    # Build the model before inspecting or saving its weights.
    example_graph, _ = training_data[0]
    model(example_graph)

    print("TensorFlow:", tf.__version__)
    print("Training graphs:", len(training_data))
    print("Validation graphs:", len(validation_data))
    print("Nodes per graph:", NODES_PER_GRAPH)
    print("Trainable parameters:", model.count_params())

    optimizer = tf.keras.optimizers.Adam(
        learning_rate=LEARNING_RATE
    )
    loss_function = tf.keras.losses.BinaryCrossentropy()

    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0

        for graph, labels in training_data:
            with tf.GradientTape() as tape:
                predictions = model(graph, training=True)
                loss = loss_function(labels, predictions)

            gradients = tape.gradient(
                loss,
                model.trainable_variables,
            )

            optimizer.apply_gradients(
                zip(gradients, model.trainable_variables)
            )

            total_loss += float(loss.numpy())

        if epoch == 1 or epoch % 5 == 0:
            validation_loss, validation_accuracy = evaluate(
                model,
                validation_data,
                loss_function,
            )

            print(
                f"Epoch {epoch:02d}/{EPOCHS} | "
                f"train_loss={total_loss / len(training_data):.4f} | "
                f"val_loss={validation_loss:.4f} | "
                f"val_accuracy={validation_accuracy:.3f}"
            )

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_weights(CHECKPOINT_PATH)

    print("\nTraining complete.")
    print("Checkpoint saved to:", CHECKPOINT_PATH)


if __name__ == "__main__":
    main()
