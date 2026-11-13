from weather.era5_reader import ERA5Reader


FILE_PATH = r"D:\WeatherData\ERA5\raw\temperature_2015_2019.nc"


reader = ERA5Reader(FILE_PATH)

reader.open()

print("ERA5 opened successfully.")

temperature = reader.get_value(
    "t2m",
    "2015-01-01T00:00:00",
    20.5937,
    78.9629
)

print()
print("Requested location:")
print("Latitude:", temperature["requested_latitude"])
print("Longitude:", temperature["requested_longitude"])

print()
print("ERA5 grid point:")
print("Latitude:", temperature["latitude"])
print("Longitude:", temperature["longitude"])

print()
print("Time:", temperature["time"])

print()
print("Temperature:", temperature["value"])
print("Temperature °C:", temperature["value"] - 273.15)

reader.close()

print()
print("ERA5 closed.")