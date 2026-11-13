from weather.weather_coordinate import WeatherCoordinate
from weather.weather_time import WeatherTime
from weather.weather_state import WeatherState


class SpatioTemporalWeather:
    """
    Represents weather data in both spatial and temporal
    dimensions.

    This class connects:
        - geographic location
        - timestamp
        - atmospheric weather state

    It does not store the complete ERA5 dataset.
    Weather data is requested from WeatherDataset when needed.
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def get_state(
        self,
        time,
        latitude,
        longitude
    ):
        """
        Retrieve the complete weather state at a
        geographic location and timestamp.
        """

        state = self.dataset.get_state(
            time=time,
            latitude=latitude,
            longitude=longitude
        )

        coordinate = WeatherCoordinate(
            latitude=latitude,
            longitude=longitude
        )

        weather_time = WeatherTime(
            value=state.time
        )

        return {
            "coordinate": coordinate,
            "time": weather_time,
            "state": state
        }

    def get_grid_location(
        self,
        time,
        latitude,
        longitude
    ):
        """
        Resolve a geographic location and timestamp to
        the corresponding ERA5 grid location.
        """

        return self.dataset.get_grid_index(
            time=time,
            latitude=latitude,
            longitude=longitude
        )