from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


bridge = WeatherDataBridge(
    ERA5_RAW_ROOT
)

weather = WeatherDataset(
    bridge
)

weather.open()

print("Weather dataset opened.")

field = weather.get_field(
    variable="temperature",

    time="2015-01-01T00:00:00",

    min_latitude=20.0,
    max_latitude=21.0,

    min_longitude=78.0,
    max_longitude=80.0
)

print()

print("Generic weather field")

print("---------------------")

print(
    "Variable:",
    field.variable
)

print(
    "Time:",
    field.time
)

print(
    "Unit:",
    field.unit
)

print()

print(
    "Shape:",
    field.shape
)

print()

print(
    "Latitudes:",
    field.latitudes
)

print(
    "Longitudes:",
    field.longitudes
)

print()

print("Temperature values:")

print(field.data)

weather.close()

print()

print("Weather dataset closed.")