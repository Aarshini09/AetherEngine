class WeatherBaseline:
    """
    Stores historical statistical information for a
    weather variable.

    A baseline describes the normal statistical behavior
    of a variable for a particular spatial and temporal
    grouping.

    All statistical values are stored in the application's
    output unit rather than the raw data source unit.
    """

    def __init__(
        self,
        variable,
        unit,
        latitude,
        longitude,
        month,
        hour,
        mean,
        standard_deviation,
        minimum,
        maximum,
        sample_count
    ):
        self.variable = variable
        self.unit = unit

        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.month = int(month)
        self.hour = int(hour)

        self.mean = float(mean)

        self.standard_deviation = float(
            standard_deviation
        )

        self.minimum = float(minimum)
        self.maximum = float(maximum)

        self.sample_count = int(sample_count)

    def standardized_anomaly(self, value):
        """
        Calculate the standardized anomaly:

            z = (value - mean) / standard_deviation

        Returns None when the historical standard deviation
        is zero.
        """

        if self.standard_deviation == 0.0:
            return None

        return (
            value - self.mean
        ) / self.standard_deviation

    def absolute_anomaly(self, value):
        """
        Calculate the absolute anomaly:

            anomaly = value - historical_mean
        """

        return value - self.mean

    def __repr__(self):
        return (
            f"WeatherBaseline("
            f"variable={self.variable}, "
            f"unit={self.unit}, "
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"month={self.month}, "
            f"hour={self.hour}, "
            f"mean={self.mean}, "
            f"standard_deviation="
            f"{self.standard_deviation}, "
            f"minimum={self.minimum}, "
            f"maximum={self.maximum}, "
            f"sample_count={self.sample_count}"
            f")"
        )