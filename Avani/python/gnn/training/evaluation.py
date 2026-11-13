
from pathlib import Path

import tensorflow as tf

from models.weather_gnn import WeatherGNN
from training.train import make_dataset, evaluate


INPUT_FEATURES = 10
HIDDEN_DIM = 64
MESSAGE_PASSING_LAYERS = 2

CHECKPOINT_PATH = (
    Path(__file__).resolve().parents[1]
    / "checkpoints"
    / "weather_gnn.weights.h5"
)


def main():
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {CHECKPOINT_PATH}\n"
            "Run training first: python -m training.train"
        )

    model = WeatherGNN(
        input_features=INPUT_FEATURES,
        hidden_dim=HIDDEN_DIM,
        message_passing_layers=MESSAGE_PASSING_LAYERS,
    )

    test_data = make_dataset(20000, 40)
    example_graph, _ = test_data[0]

    model(example_graph)
    model.load_weights(CHECKPOINT_PATH)

    loss_function = tf.keras.losses.BinaryCrossentropy()
    test_loss, test_accuracy = evaluate(
        model,
        test_data,
        loss_function,
    )

    print("Test graphs:", len(test_data))
    print("Test loss:", round(test_loss, 4))
    print("Test accuracy:", round(test_accuracy, 4))
    print("\nNote: these results measure only the synthetic task.")


if __name__ == "__main__":
    main()
