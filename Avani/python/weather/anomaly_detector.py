from weather.weather_anomaly import WeatherAnomaly


class AnomalyDetector:
    """
    Detects weather anomalies by comparing an observation
    against a historical WeatherBaseline.

    The initial detector uses a standardized anomaly
    (z-score) threshold.

        z = (value - baseline_mean) / baseline_std

    An observation is considered anomalous when:

        |z| >= threshold
    """

    def __init__(
        self,
        threshold=2.0
    ):
        self.threshold = float(
            threshold
        )

    def detect(
        self,
        variable,
        time,
        latitude,
        longitude,
        value,
        baseline
    ):
        """
        Compare one weather observation against a
        historical baseline.

        Returns:
            WeatherAnomaly
        """

        if baseline is None:
            raise ValueError(
                "A historical baseline is required."
            )

        absolute_anomaly = (
            baseline.absolute_anomaly(
                value
            )
        )

        standardized_anomaly = (
            baseline.standardized_anomaly(
                value
            )
        )

        if standardized_anomaly is None:

            is_anomaly = False
            severity = "undefined"

        else:

            magnitude = abs(
                standardized_anomaly
            )

            is_anomaly = (
                magnitude >= self.threshold
            )

            severity = self._classify_severity(
                magnitude
            )

        return WeatherAnomaly(
            variable=variable,
            time=time,
            latitude=latitude,
            longitude=longitude,
            value=value,

            baseline_mean=baseline.mean,

            baseline_standard_deviation=(
                baseline.standard_deviation
            ),

            absolute_anomaly=absolute_anomaly,

            standardized_anomaly=(
                standardized_anomaly
            ),

            is_anomaly=is_anomaly,

            severity=severity
        )

    def _classify_severity(
        self,
        magnitude
    ):
        """
        Classify anomaly severity using the absolute
        standardized anomaly.

        Current prototype:

            < 2σ   → normal
            2–3σ   → moderate
            3–4σ   → severe
            >= 4σ  → extreme
        """

        if magnitude < 2.0:
            return "normal"

        if magnitude < 3.0:
            return "moderate"

        if magnitude < 4.0:
            return "severe"

        return "extreme"