from config import ERA5_RAW_ROOT

from weather.era5_reader import ERA5Reader
from weather.weather_grid_index import WeatherGridIndex


temperature_file = (
    ERA5_RAW_ROOT /
    "temperature_2015_2019.nc"
)


reader = ERA5Reader(temperature_file)

reader.open()


grid_index = WeatherGridIndex(reader)

grid_index.initialize()


print("Weather grid index test")
print()


latitude = 20.5937
longitude = 78.9629
time = "2015-01-01T00:00:00"


print("Requested:")
print(f"  Latitude:  {latitude}")
print(f"  Longitude: {longitude}")
print(f"  Time:      {time}")

print()


result = grid_index.get_grid_index(
    time=time,
    latitude=latitude,
    longitude=longitude
)


print("Resolved ERA5 grid:")
print(
    f"  Time index:       {result['time_index']}"
)

print(
    f"  Latitude index:   {result['latitude_index']}"
)

print(
    f"  Longitude index:  {result['longitude_index']}"
)

print()

print(
    f"  Latitude:         {result['latitude']}"
)

print(
    f"  Longitude:        {result['longitude']}"
)

print(
    f"  Time:             {result['time']}"
)


reader.close()

print()
print("Weather grid index test complete.")