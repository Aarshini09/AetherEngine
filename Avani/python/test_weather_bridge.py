from config import ERA5_RAW_ROOT

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


bridge = WeatherDataBridge(ERA5_RAW_ROOT)

weather = WeatherDataset(bridge)

weather.open()

print("Weather data bridge opened.")
print()


time = "2015-01-01T00:00:00"

latitude = 20.5937
longitude = 78.9629


variables = [
    "temperature",
    "dewpoint",
    "mean_sea_level_pressure",
    "wind_u",
    "surface_pressure",
    "wind_v",
    "total_precipitation"
]


for variable in variables:

    value = weather.get_value(
        variable=variable,
        time=time,
        latitude=latitude,
        longitude=longitude
    )

    print(
        f"{variable:28} "
        f"{value.value:.4f} {value.unit}"
    )


weather.close()

print()
print("Weather data bridge closed.")