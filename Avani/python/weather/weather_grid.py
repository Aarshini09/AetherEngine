from weather.weather_field import WeatherField


class WeatherGrid:
    """
    Provides access to weather fields over a spatial region.

    WeatherGrid does not own or duplicate the complete
    ERA5 dataset. It requests only the region needed.
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def get_field(
        self,
        variable,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Retrieve a weather field for a spatial region
        at one point in time.
        """

        return self.dataset.get_field(
            variable=variable,
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude
        )

    def get_temperature(
        self,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Retrieve a temperature field over a region.
        """

        return self.get_field(
            variable="temperature",
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude
        )

    def get_wind_u(
        self,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Retrieve the U-component of wind over a region.
        """

        return self.get_field(
            variable="wind_u",
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude
        )

    def get_wind_v(
        self,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Retrieve the V-component of wind over a region.
        """

        return self.get_field(
            variable="wind_v",
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude
        )