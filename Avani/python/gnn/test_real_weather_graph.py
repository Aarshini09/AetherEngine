
from datetime import datetime

import tensorflow as tf

from application.avani_application import AvaniApplication
from weather.weather_data_index import WeatherDataIndex
from weather.weather_data_graph_builder import WeatherDataGraphBuilder

from gnn.data.weather_graph_adapter import (
    FEATURE_COUNT,
    WeatherGraphAdapter,
)
from gnn.models.weather_gnn import WeatherGNN


WEATHER_DATA_ROOT = r"D:\WeatherData\ERA5\raw"

# Keep the first test deliberately small.
REGION = {
    "min_latitude": 20.0,
    "max_latitude": 22.0,
    "min_longitude": 78.0,
    "max_longitude": 80.0,
}

# Replace this with a timestamp known to exist in your ERA5 files.
TEST_TIME = datetime(2019, 7, 15, 12, 0)


def main():
    application = AvaniApplication(WEATHER_DATA_ROOT)

    try:
        application.initialize()

        dataset = application.weather_dataset

        # Create an independent index; do not overwrite the
        # application's active analysis index.
        data_index = WeatherDataIndex(dataset.grid_index)

        data_index.build(**REGION)

        node_count = data_index.get_node_count()

        if node_count == 0:
            raise RuntimeError(
                "The selected region contains no weather grid nodes."
            )

        print("Selected region nodes:", node_count)
        print("Requested timestamp:", TEST_TIME.isoformat())

        graph_builder = WeatherDataGraphBuilder(
            weather_dataset=dataset,
            data_index=data_index,
        )

        graph = graph_builder.build(times=[TEST_TIME])

        inputs, metadata = WeatherGraphAdapter.convert(
            graph,
            TEST_TIME,
        )

        print("Node feature shape:", inputs["node_features"].shape)
        print("Edge index shape:", inputs["edge_index"].shape)
        print("Feature order:", metadata["feature_names"])

        model = WeatherGNN(input_features=FEATURE_COUNT)
        scores = model(inputs, training=False)

        print("GNN output shape:", scores.shape)
        print("First five node IDs:", metadata["node_ids"][:5])
        print(
            "First five raw scores:",
            tf.squeeze(scores[:5], axis=-1).numpy(),
        )

        print("\nReal ERA5 graph smoke test passed.")
        print(
            "Scores are from an untrained model and are not "
            "meaningful anomaly probabilities."
        )

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
