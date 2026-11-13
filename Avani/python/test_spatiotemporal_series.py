from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_spatiotemporal import SpatioTemporalWeather
from weather.spatiotemporal_series import SpatioTemporalSeries


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather_dataset = WeatherDataset(bridge)

weather_dataset.open()

weather = SpatioTemporalWeather(
    weather_dataset
)

series = SpatioTemporalSeries(
    weather
)


print("Spatio-Temporal Series test")
print()


times = [
    "2015-01-01T00:00:00",
    "2015-01-01T06:00:00",
    "2015-01-01T12:00:00",
    "2015-01-01T18:00:00"
]


series.load(
    latitude=20.5937,
    longitude=78.9629,
    times=times
)


print("Location:")
print(
    f"  Latitude:  {series.coordinate.latitude}"
)

print(
    f"  Longitude: {series.coordinate.longitude}"
)

print()

print(
    f"Number of timestamps: {len(series)}"
)

print()

for index, result in enumerate(series.get_states()):

    state = result["state"]
    time = result["time"]

    print(f"Time {index}: {time.value}")

    print(
        f"  Temperature: "
        f"{state.temperature:.4f} °C"
    )

    print(
        f"  Pressure:    "
        f"{state.mean_sea_level_pressure:.4f} hPa"
    )

    print(
        f"  Wind speed:  "
        f"{state.wind_speed:.4f} m/s"
    )

    print(
        f"  Precipitation: "
        f"{state.total_precipitation:.4f} mm"
    )

    print()


weather_dataset.close()

print("Spatio-temporal series test complete.")