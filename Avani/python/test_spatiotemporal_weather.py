from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_spatiotemporal import SpatioTemporalWeather


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather_dataset = WeatherDataset(bridge)

weather_dataset.open()

weather = SpatioTemporalWeather(
    weather_dataset
)


print("Spatio-Temporal Weather test")
print()


result = weather.get_state(
    time="2015-01-01T00:00:00",
    latitude=20.5937,
    longitude=78.9629
)


coordinate = result["coordinate"]
weather_time = result["time"]
state = result["state"]


print("Requested location:")
print(
    f"  Latitude:  {coordinate.latitude}"
)

print(
    f"  Longitude: {coordinate.longitude}"
)

print()

print("Time:")
print(
    f"  {weather_time.value}"
)

print()

print("Weather state:")
print(
    f"  Temperature:          "
    f"{state.temperature:.4f} °C"
)

print(
    f"  Dewpoint:             "
    f"{state.dewpoint:.4f} °C"
)

print(
    f"  Mean sea level press: "
    f"{state.mean_sea_level_pressure:.4f} hPa"
)

print(
    f"  Surface pressure:     "
    f"{state.surface_pressure:.4f} hPa"
)

print(
    f"  Wind U:               "
    f"{state.wind_u:.4f} m/s"
)

print(
    f"  Wind V:               "
    f"{state.wind_v:.4f} m/s"
)

print(
    f"  Wind speed:           "
    f"{state.wind_speed:.4f} m/s"
)

print(
    f"  Precipitation:        "
    f"{state.total_precipitation:.4f} mm"
)

print()

grid_location = weather.get_grid_location(
    time="2015-01-01T00:00:00",
    latitude=20.5937,
    longitude=78.9629
)


print("Resolved ERA5 grid:")
print(
    f"  Time index:       "
    f"{grid_location['time_index']}"
)

print(
    f"  Latitude index:   "
    f"{grid_location['latitude_index']}"
)

print(
    f"  Longitude index:  "
    f"{grid_location['longitude_index']}"
)

print(
    f"  Grid latitude:    "
    f"{grid_location['latitude']}"
)

print(
    f"  Grid longitude:   "
    f"{grid_location['longitude']}"
)

print()

weather_dataset.close()

print("Spatio-temporal weather test complete.")