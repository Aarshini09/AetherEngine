from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_data_index import WeatherDataIndex
from weather.weather_data_graph_builder import (
    WeatherDataGraphBuilder
)


bridge = WeatherDataBridge(
    ERA5_RAW_ROOT
)

weather_dataset = WeatherDataset(
    bridge
)

weather_dataset.open()


data_index = WeatherDataIndex(
    weather_dataset._grid_index
)


data_index.build(
    min_latitude=20.0,
    max_latitude=21.0,
    min_longitude=78.0,
    max_longitude=80.0
)


times = [
    "2015-01-01T00:00:00",
    "2015-01-01T06:00:00",
    "2015-01-01T12:00:00",
    "2015-01-01T18:00:00"
]


builder = WeatherDataGraphBuilder(
    weather_dataset=weather_dataset,
    data_index=data_index
)


graph = builder.build(
    times=times
)


print("Weather Data Graph API test")
print()

print(
    f"Spatial nodes: "
    f"{graph.get_node_count()}"
)

print(
    f"Weather states: "
    f"{graph.get_state_count()}"
)

print(
    f"Temporal edges: "
    f"{graph.get_temporal_edge_count()}"
)

print()


# ---------------------------------------------------------
# Test spatial queries
# ---------------------------------------------------------

node_id = 0

node = graph.get_node(
    node_id
)

print("Node query:")
print(
    f"  ID:        {node.node_id}"
)

print(
    f"  Latitude:  "
    f"{node.coordinate.latitude}"
)

print(
    f"  Longitude: "
    f"{node.coordinate.longitude}"
)

print()


neighbor_ids = graph.get_spatial_neighbor_ids(
    node_id
)

print(
    f"Spatial neighbor IDs: "
    f"{neighbor_ids}"
)

print()


# ---------------------------------------------------------
# Test temporal queries
# ---------------------------------------------------------

print("Temporal traversal:")

current_time = times[0]

while current_time is not None:

    next_time = graph.get_next_time(
        node_id,
        current_time
    )

    print(
        f"  {current_time} → {next_time}"
    )

    current_time = next_time


print()


# ---------------------------------------------------------
# Test state query
# ---------------------------------------------------------

state = graph.get_state(
    node_id=node_id,
    time=times[0]
)

print("State query:")

print(
    f"  Temperature: "
    f"{state.temperature:.4f} °C"
)

print(
    f"  Pressure: "
    f"{state.mean_sea_level_pressure:.4f} hPa"
)

print(
    f"  Wind speed: "
    f"{state.wind_speed:.4f} m/s"
)

print()


# ---------------------------------------------------------
# Test combined state traversal
# ---------------------------------------------------------

connected = graph.get_connected_state(
    node_id=node_id,
    time=times[0]
)

print("Connected state query:")

print(
    f"  Current time: "
    f"{connected['current_time']}"
)

print(
    f"  Next time: "
    f"{connected['next_time']}"
)

print(
    f"  Current temperature: "
    f"{connected['current_state'].temperature:.4f} °C"
)

print(
    f"  Next temperature: "
    f"{connected['next_state'].temperature:.4f} °C"
)

print()


# ---------------------------------------------------------
# Verification
# ---------------------------------------------------------

expected_states = (
    data_index.get_node_count()
    * len(times)
)

expected_temporal_edges = (
    data_index.get_node_count()
    * (len(times) - 1)
)


if graph.get_state_count() != expected_states:

    raise RuntimeError(
        "Weather state count verification failed."
    )


if (
    graph.get_temporal_edge_count()
    != expected_temporal_edges
):

    raise RuntimeError(
        "Temporal edge count verification failed."
    )


if neighbor_ids != [9, 1]:

    raise RuntimeError(
        "Spatial neighbor query verification failed."
    )


if (
    graph.get_next_time(
        node_id,
        times[0]
    )
    != times[1]
):

    raise RuntimeError(
        "Temporal traversal verification failed."
    )


print(
    "State count verification: PASS"
)

print(
    "Temporal edge verification: PASS"
)

print(
    "Spatial query verification: PASS"
)

print(
    "Temporal query verification: PASS"
)

print(
    "Combined state query verification: PASS"
)


weather_dataset.close()

print()

print(
    "Weather Data Graph API test complete."
)