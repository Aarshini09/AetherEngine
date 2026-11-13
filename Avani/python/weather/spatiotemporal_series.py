from weather.weather_coordinate import WeatherCoordinate
from weather.weather_time import WeatherTime


class SpatioTemporalSeries:
    """
    Represents a sequence of weather states for one
    geographic location across multiple timestamps.

    The class stores the requested location and the
    retrieved weather states. It does not load the
    complete ERA5 dataset into memory.
    """

    def __init__(self, weather):
        self.weather = weather

        self.coordinate = None
        self.states = []

    def load(
        self,
        latitude,
        longitude,
        times
    ):
        """
        Load weather states for one location across
        a sequence of timestamps.
        """

        self.coordinate = WeatherCoordinate(
            latitude=latitude,
            longitude=longitude
        )

        self.states = []

        for time in times:
            result = self.weather.get_state(
                time=time,
                latitude=latitude,
                longitude=longitude
            )

            self.states.append(result)

    def get_states(self):
        """
        Return all weather states in the series.
        """

        return self.states

    def get_state(self, index):
        """
        Return one weather state by its temporal index.
        """

        return self.states[index]

    def __len__(self):
        """
        Return the number of timestamps in the series.
        """

        return len(self.states)