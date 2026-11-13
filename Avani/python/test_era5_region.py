from weather.era5_reader import ERA5Reader


FILE_PATH = r"D:\WeatherData\ERA5\raw\temperature_2015_2019.nc"


reader = ERA5Reader(FILE_PATH)

reader.open()

print("ERA5 opened successfully.")

region = reader.get_region(
    "t2m",
    "2015-01-01T00:00:00",
    20.0,
    21.0,
    78.0,
    80.0
)

print()
print("Region:")
print("Latitude: 20.0 -> 21.0")
print("Longitude: 78.0 -> 80.0")

print()
print("Region shape:", region.shape)

print()
print("Coordinates:")
print("Latitudes:", region.latitude.values)
print("Longitudes:", region.longitude.values)

reader.close()

print()
print("ERA5 closed.")