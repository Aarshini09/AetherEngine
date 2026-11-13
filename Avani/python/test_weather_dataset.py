# from weather.era5_reader import ERA5Reader
# from weather.weather_dataset import WeatherDataset


# FILE_PATH = r"D:\WeatherData\ERA5\raw\temperature_2015_2019.nc"


# reader = ERA5Reader(FILE_PATH)

# weather = WeatherDataset(reader)

# weather.open()

# print("Weather dataset opened.")

# temperature = weather.get_temperature(
#     "2015-01-01T00:00:00",
#     20.5937,
#     78.9629
# )

# print()
# print("Temperature query")
# print("-----------------")

# print(
#     "Requested latitude:",
#     temperature.requested_latitude
# )

# print(
#     "Requested longitude:",
#     temperature.requested_longitude
# )

# print()
# print("ERA5 grid point")
# print("----------------")

# print(
#     "Latitude:",
#     temperature.latitude
# )

# print(
#     "Longitude:",
#     temperature.longitude
# )

# print()
# print("Temperature")
# print("-----------")

# print(
#     "Value:",
#     temperature.value,
#     temperature.unit
# )

# weather.close()

# print()
# print("Weather dataset closed.")


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


temperature = weather.get_temperature(
    time="2015-01-01T00:00:00",
    latitude=20.5937,
    longitude=78.9629
)


print("Weather Dataset test")
print()

print(
    f"Temperature: {temperature.value:.4f} "
    f"{temperature.unit}"
)

print(
    f"Requested location: "
    f"{temperature.requested_latitude}, "
    f"{temperature.requested_longitude}"
)

print(
    f"ERA5 location: "
    f"{temperature.latitude}, "
    f"{temperature.longitude}"
)

print(
    f"Time: {temperature.time}"
)

weather.close()

print()
print("Weather Dataset test complete.")