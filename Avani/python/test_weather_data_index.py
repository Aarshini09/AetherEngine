from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_grid import WeatherGrid
from weather.weather_data_index import WeatherDataIndex


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather_dataset = WeatherDataset(bridge)

weather_dataset.open()


index = WeatherDataIndex(
    weather_dataset._grid_index
)


index.build(
    min_latitude=20.0,
    max_latitude=21.0,
    min_longitude=78.0,
    max_longitude=80.0
)


print("Weather Data Index test")
print()

print(
    f"Number of nodes: "
    f"{index.get_node_count()}"
)

print()


for node_id in range(
    min(5, index.get_node_count())
):

    node = index.get_node(node_id)

    print(f"Node {node.node_id}")

    print(
        f"  Latitude:       "
        f"{node.coordinate.latitude}"
    )

    print(
        f"  Longitude:      "
        f"{node.coordinate.longitude}"
    )

    print(
        f"  Latitude index: "
        f"{node.latitude_index}"
    )

    print(
        f"  Longitude index:"
        f" {node.longitude_index}"
    )

    print(
        f"  Neighbors:      "
        f"{node.neighbors}"
    )

    print()


weather_dataset.close()

print(
    "Weather data index test complete."
)