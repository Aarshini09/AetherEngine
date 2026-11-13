from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather = WeatherDataset(bridge)

weather.open()

print("Weather state test")
print()


state = weather.get_state(
    time="2015-01-01T00:00:00",
    latitude=20.5937,
    longitude=78.9629
)


print(f"Time:                 {state.time}")
print(
    f"Location:             "
    f"{state.latitude}, {state.longitude}"
)

print()

print(f"Temperature:          {state.temperature:.4f} °C")
print(f"Dewpoint:             {state.dewpoint:.4f} °C")
print(
    f"Mean sea level press: "
    f"{state.mean_sea_level_pressure:.4f} hPa"
)
print(
    f"Surface pressure:     "
    f"{state.surface_pressure:.4f} hPa"
)

print()

print(f"Wind U:               {state.wind_u:.4f} m/s")
print(f"Wind V:               {state.wind_v:.4f} m/s")
print(f"Wind speed:           {state.wind_speed:.4f} m/s")

print()

print(
    f"Total precipitation:  "
    f"{state.total_precipitation:.4f} mm"
)


weather.close()

print()
print("Weather state test complete.")