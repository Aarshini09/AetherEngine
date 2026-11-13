from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_data_index import WeatherDataIndex
from weather.weather_data_graph import WeatherDataGraph


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


graph = WeatherDataGraph(
    data_index
)

graph.initialize()


print("Weather Data Graph test")
print()

print(
    f"Spatial nodes: "
    f"{graph.get_node_count()}"
)

print(
    f"Weather states: "
    f"{graph.get_state_count()}"
)

print()


times = [
    "2015-01-01T00:00:00",
    "2015-01-01T06:00:00",
    "2015-01-01T12:00:00",
    "2015-01-01T18:00:00"
]


# Use one spatial node for the first test.

node_id = 0

node = data_index.get_node(
    node_id
)


print("Selected node:")
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


# Retrieve the real weather states from ERA5.

for time in times:

    state = weather_dataset.get_state(
        time=time,
        latitude=node.coordinate.latitude,
        longitude=node.coordinate.longitude
    )

    graph.add_state(
        node_id=node_id,
        time=time,
        state=state
    )


print(
    f"States stored for node {node_id}: "
    f"{len(graph.get_node_series(node_id))}"
)

print()


series = graph.get_node_series(
    node_id
)


for time in series.get_times():

    state = series.get_state(
        time
    )

    print(
        f"{time}  "
        f"Temperature: "
        f"{state.temperature:.4f} °C  "
        f"Wind: "
        f"{state.wind_speed:.4f} m/s"
    )


print()

print(
    f"Total graph states: "
    f"{graph.get_state_count()}"
)


weather_dataset.close()

print()

print(
    "Weather data graph test complete."
)