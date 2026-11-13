class WeatherState:
    """
    Represents the atmospheric state at one location
    and one point in time.

    A WeatherState contains application-level weather
    variables after unit conversion.
    """

    def __init__(
        self,
        time,
        latitude,
        longitude,
        temperature,
        dewpoint,
        mean_sea_level_pressure,
        surface_pressure,
        wind_u,
        wind_v,
        total_precipitation
    ):
        self.time = time

        self.latitude = latitude
        self.longitude = longitude

        self.temperature = temperature
        self.dewpoint = dewpoint

        self.mean_sea_level_pressure = mean_sea_level_pressure
        self.surface_pressure = surface_pressure

        self.wind_u = wind_u
        self.wind_v = wind_v

        self.total_precipitation = total_precipitation

    @property
    def wind_speed(self):
        """
        Calculate horizontal wind speed from the
        U and V wind components.

        speed = sqrt(u² + v²)
        """

        return (
            self.wind_u ** 2 +
            self.wind_v ** 2
        ) ** 0.5

    def __repr__(self):
        return (
            f"WeatherState("
            f"time={self.time}, "
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"temperature={self.temperature}, "
            f"dewpoint={self.dewpoint}, "
            f"mean_sea_level_pressure={self.mean_sea_level_pressure}, "
            f"surface_pressure={self.surface_pressure}, "
            f"wind_u={self.wind_u}, "
            f"wind_v={self.wind_v}, "
            f"total_precipitation={self.total_precipitation}"
            f")"
        )