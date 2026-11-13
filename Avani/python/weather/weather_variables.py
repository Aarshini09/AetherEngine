from weather.weather_variable import WeatherVariable


def kelvin_to_celsius(data):
    """Convert temperature from Kelvin to Celsius."""

    return data - 273.15


def pascal_to_hectopascal(data):
    """Convert pressure from Pascal to hectopascal."""

    return data / 100.0


def meters_to_millimeters(data):
    """Convert precipitation from metres to millimetres."""

    return data * 1000.0


def identity(data):
    """Return data without changing its numerical value."""

    return data


TEMPERATURE = WeatherVariable(
    name="temperature",
    source_name="t2m",
    input_unit="K",
    output_unit="°C",
    conversion=kelvin_to_celsius
)


DEWPOINT = WeatherVariable(
    name="dewpoint",
    source_name="d2m",
    input_unit="K",
    output_unit="°C",
    conversion=kelvin_to_celsius
)


MEAN_SEA_LEVEL_PRESSURE = WeatherVariable(
    name="mean_sea_level_pressure",
    source_name="msl",
    input_unit="Pa",
    output_unit="hPa",
    conversion=pascal_to_hectopascal
)


SURFACE_PRESSURE = WeatherVariable(
    name="surface_pressure",
    source_name="sp",
    input_unit="Pa",
    output_unit="hPa",
    conversion=pascal_to_hectopascal
)


WIND_U = WeatherVariable(
    name="wind_u",
    source_name="u10",
    input_unit="m/s",
    output_unit="m/s",
    conversion=identity
)


WIND_V = WeatherVariable(
    name="wind_v",
    source_name="v10",
    input_unit="m/s",
    output_unit="m/s",
    conversion=identity
)


TOTAL_PRECIPITATION = WeatherVariable(
    name="total_precipitation",
    source_name="tp",
    input_unit="m",
    output_unit="mm",
    conversion=meters_to_millimeters
)


WEATHER_VARIABLES = {
    TEMPERATURE.name: TEMPERATURE,
    DEWPOINT.name: DEWPOINT,
    MEAN_SEA_LEVEL_PRESSURE.name: MEAN_SEA_LEVEL_PRESSURE,
    SURFACE_PRESSURE.name: SURFACE_PRESSURE,
    WIND_U.name: WIND_U,
    WIND_V.name: WIND_V,
    TOTAL_PRECIPITATION.name: TOTAL_PRECIPITATION
}