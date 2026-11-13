from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather = WeatherDataset(bridge)

weather.open()

print("WeatherDataset grid index test")
print()


latitude = 20.5937
longitude = 78.9629
time = "2015-01-01T00:00:00"


print("Requested:")
print(f"  Latitude:  {latitude}")
print(f"  Longitude: {longitude}")
print(f"  Time:      {time}")

print()


result = weather.get_grid_index(
    time=time,
    latitude=latitude,
    longitude=longitude
)


print("Resolved ERA5 grid:")
print(f"  Time index:       {result['time_index']}")
print(f"  Latitude index:   {result['latitude_index']}")
print(f"  Longitude index:  {result['longitude_index']}")

print()

print(f"  Latitude:         {result['latitude']}")
print(f"  Longitude:        {result['longitude']}")
print(f"  Time:             {result['time']}")


weather.close()

print()
print("WeatherDataset grid index test complete.")