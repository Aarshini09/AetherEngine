class SpatioTemporalGrid:
    """
    Represents weather fields across multiple timestamps.

    Each timestamp contains a spatial WeatherField.

    The class does not load the complete ERA5 dataset
    into memory at construction time.
    """

    def __init__(self, grid):
        self.grid = grid

        self.times = []
        self.fields = {}

    def load(
        self,
        variable,
        times,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Load a spatial weather field for each requested
        timestamp.
        """

        self.times = list(times)
        self.fields = {}

        for time in self.times:

            field = self.grid.get_field(
                variable=variable,
                time=time,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude
            )

            self.fields[time] = field

    def get_field(self, time):
        """
        Return the weather field associated with a timestamp.
        """

        if time not in self.fields:
            raise KeyError(
                f"No weather field loaded for time: {time}"
            )

        return self.fields[time]

    def get_times(self):
        """
        Return all timestamps represented by the grid.
        """

        return self.times

    def __len__(self):
        """
        Return the number of timestamps.
        """

        return len(self.times)