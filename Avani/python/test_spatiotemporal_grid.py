from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_grid import WeatherGrid
from weather.spatiotemporal_grid import SpatioTemporalGrid


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather_dataset = WeatherDataset(bridge)

weather_dataset.open()

weather_grid = WeatherGrid(
    weather_dataset
)

grid = SpatioTemporalGrid(
    weather_grid
)


print("Spatio-Temporal Grid test")
print()


times = [
    "2015-01-01T00:00:00",
    "2015-01-01T06:00:00",
    "2015-01-01T12:00:00",
    "2015-01-01T18:00:00"
]


grid.load(
    variable="temperature",
    times=times,

    min_latitude=20.0,
    max_latitude=21.0,

    min_longitude=78.0,
    max_longitude=80.0
)


print(
    f"Number of timestamps: {len(grid)}"
)

print()


for time in grid.get_times():

    field = grid.get_field(time)

    print(f"Time: {time}")

    print(
        f"  Variable: {field.variable}"
    )

    print(
        f"  Unit:     {field.unit}"
    )

    print(
        f"  Shape:    {field.shape}"
    )

    print(
        f"  Min:      {field.data.min():.4f}"
    )

    print(
        f"  Max:      {field.data.max():.4f}"
    )

    print()


weather_dataset.close()

print(
    "Spatio-temporal grid test complete."
)