class WeatherAnomaly:
    """
    Represents a detected weather anomaly at a specific
    location and timestamp.

    A WeatherAnomaly stores the observation, its historical
    baseline, and the resulting anomaly measurements.

    This class does not decide whether an observation is
    anomalous. That decision is made by AnomalyDetector.
    """

    def __init__(
        self,
        variable,
        time,
        latitude,
        longitude,
        value,
        baseline_mean,
        baseline_standard_deviation,
        absolute_anomaly,
        standardized_anomaly,
        is_anomaly,
        severity
    ):
        self.variable = variable
        self.time = time

        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.value = float(value)

        self.baseline_mean = float(
            baseline_mean
        )

        self.baseline_standard_deviation = float(
            baseline_standard_deviation
        )

        self.absolute_anomaly = float(
            absolute_anomaly
        )

        self.standardized_anomaly = (
            None
            if standardized_anomaly is None
            else float(standardized_anomaly)
        )

        self.is_anomaly = bool(
            is_anomaly
        )

        self.severity = severity

    def __repr__(self):
        return (
            f"WeatherAnomaly("
            f"variable={self.variable}, "
            f"time={self.time}, "
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"value={self.value}, "
            f"baseline_mean={self.baseline_mean}, "
            f"absolute_anomaly="
            f"{self.absolute_anomaly}, "
            f"standardized_anomaly="
            f"{self.standardized_anomaly}, "
            f"is_anomaly={self.is_anomaly}, "
            f"severity={self.severity}"
            f")"
        )