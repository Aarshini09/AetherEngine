
import tensorflow as tf

from gnn.data.weather_graph_adapter import (
    FEATURE_COUNT,
    WeatherGraphAdapter,
)


def test_adapter(graph, time):
    inputs, metadata = WeatherGraphAdapter.convert(graph, time)

    node_count = graph.get_node_count()
    edge_count = int(tf.shape(inputs["edge_index"])[1].numpy())

    assert tuple(inputs["node_features"].shape) == (
        node_count,
        FEATURE_COUNT,
    )

    assert inputs["edge_index"].shape[0] == 2
    assert len(metadata["node_ids"]) == node_count

    print("Timestamp:", metadata["time"])
    print("Nodes:", node_count)
    print("Edges:", edge_count)
    print("Features per node:", FEATURE_COUNT)
    print("Node feature tensor:", inputs["node_features"].shape)
    print("Edge tensor:", inputs["edge_index"].shape)

    # Feed the real-data tensors into the existing model.
    from gnn.models.weather_gnn import WeatherGNN

    model = WeatherGNN(input_features=FEATURE_COUNT)
    scores = model(inputs, training=False)

    print("GNN output shape:", scores.shape)
    print("Adapter smoke test passed.")

    return scores, metadata
