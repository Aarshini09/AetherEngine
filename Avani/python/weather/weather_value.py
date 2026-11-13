class WeatherValue:
    """
    Represents one weather measurement at a specific
    location and time.
    """

    def __init__(
        self,
        variable,
        time,
        requested_latitude,
        requested_longitude,
        latitude,
        longitude,
        value,
        unit
    ):
        self.variable = variable
        self.time = time

        self.requested_latitude = requested_latitude
        self.requested_longitude = requested_longitude

        self.latitude = latitude
        self.longitude = longitude

        self.value = value
        self.unit = unit