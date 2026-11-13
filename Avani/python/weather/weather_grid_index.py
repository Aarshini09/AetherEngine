import numpy as np

from weather.weather_coordinate import WeatherCoordinate
from weather.weather_time import WeatherTime


class WeatherGridIndex:
    """
    Provides spatial and temporal indexing for an ERA5
    weather dataset.

    The index stores only coordinates and timestamps.
    It does not load weather variables into memory.
    """

    def __init__(self, reader):
        self.reader = reader

        self._latitudes = None
        self._longitudes = None
        self._times = None

    def initialize(self):
        """
        Load the ERA5 coordinate arrays needed for indexing.

        Only coordinate information is loaded, not the
        weather fields themselves.
        """

        self._latitudes = np.asarray(
            self.reader.get_latitudes().values
        )

        self._longitudes = np.asarray(
            self.reader.get_longitudes().values
        )

        self._times = np.asarray(
            self.reader.get_times().values
        )

    def get_coordinate(self, latitude, longitude):
        """
        Find the nearest ERA5 grid coordinate.

        Returns:
            WeatherCoordinate
        """

        self._ensure_initialized()

        latitude_index = self._find_nearest_index(
            self._latitudes,
            latitude
        )

        longitude_index = self._find_nearest_index(
            self._longitudes,
            longitude % 360.0
        )

        return WeatherCoordinate(
            latitude=self._latitudes[latitude_index],
            longitude=self._longitudes[longitude_index]
        )

    def get_spatial_index(self, latitude, longitude):
        """
        Find the nearest ERA5 latitude and longitude indices.

        Returns:
            Dictionary containing requested coordinate,
            selected coordinate, and grid indices.
        """

        self._ensure_initialized()

        requested_longitude = longitude
        era5_longitude = longitude % 360.0

        latitude_index = self._find_nearest_index(
            self._latitudes,
            latitude
        )

        longitude_index = self._find_nearest_index(
            self._longitudes,
            era5_longitude
        )

        return {
            "requested_latitude": latitude,
            "requested_longitude": requested_longitude,

            "latitude_index": latitude_index,
            "longitude_index": longitude_index,

            "latitude": float(
                self._latitudes[latitude_index]
            ),
            "longitude": float(
                self._longitudes[longitude_index]
            )
        }

    def get_time(self, time):
        """
        Find the nearest ERA5 timestamp.

        Returns:
            WeatherTime
        """

        self._ensure_initialized()

        requested_time = np.datetime64(time)

        time_index = self._find_nearest_datetime_index(
            self._times,
            requested_time
        )

        return WeatherTime(
            value=self._times[time_index],
            index=time_index
        )

    def get_time_index(self, time):
        """
        Return the index of the nearest ERA5 timestamp.
        """

        weather_time = self.get_time(time)

        return weather_time.index

    def get_grid_index(
        self,
        time,
        latitude,
        longitude
    ):
        """
        Resolve a complete weather query into its
        temporal and spatial grid indices.
        """

        spatial = self.get_spatial_index(
            latitude,
            longitude
        )

        weather_time = self.get_time(time)

        return {
            "time_index": weather_time.index,
            "time": weather_time.value,

            "latitude_index": spatial["latitude_index"],
            "longitude_index": spatial["longitude_index"],

            "latitude": spatial["latitude"],
            "longitude": spatial["longitude"],

            "requested_latitude":
                spatial["requested_latitude"],

            "requested_longitude":
                spatial["requested_longitude"]
        }

    def _find_nearest_index(self, values, target):
        """
        Find the index of the value nearest to target.
        """

        return int(
            np.abs(values - target).argmin()
        )

    def _find_nearest_datetime_index(
        self,
        values,
        target
    ):
        """
        Find the index of the datetime nearest to target.
        """

        differences = np.abs(
            values - target
        )

        return int(
            differences.argmin()
        )

    def _ensure_initialized(self):
        """
        Ensure the coordinate arrays have been initialized.
        """

        if (
            self._latitudes is None
            or self._longitudes is None
            or self._times is None
        ):
            raise RuntimeError(
                "WeatherGridIndex is not initialized. "
                "Call initialize() first."
            )