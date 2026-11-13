from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_grid import WeatherGrid


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather = WeatherDataset(bridge)

weather.open()

grid = WeatherGrid(weather)


print("WeatherGrid test")
print()


field = grid.get_temperature(
    time="2015-01-01T12:00:00",
    min_latitude=20.0,
    max_latitude=21.0,
    min_longitude=78.0,
    max_longitude=80.0
)


print(f"Variable: {field.variable}")
print(f"Time:     {field.time}")
print(f"Unit:     {field.unit}")
print(f"Shape:    {field.shape}")

print()

print("Latitudes:")
print(field.latitudes)

print()

print("Longitudes:")
print(field.longitudes)

print()

print("Temperature field:")
print(field.data)


weather.close()

print()
print("WeatherGrid test complete.")