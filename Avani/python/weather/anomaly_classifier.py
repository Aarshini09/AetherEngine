from weather.weather_anomaly_classification import (
    WeatherAnomalyClassification
)


class AnomalyClassifier:
    """
    Classifies detected WeatherAnomaly objects into
    meaningful weather-event categories.

    This is the initial rule-based classifier.

    Machine-learning and GNN-based classification can
    be added later without changing the WeatherAnomaly
    representation.
    """

    def classify(
        self,
        anomaly
    ):
        """
        Classify a WeatherAnomaly.

        Returns:
            WeatherAnomalyClassification
        """

        variable = anomaly.variable

        direction = self._get_direction(
            anomaly
        )

        category = self._get_category(
            anomaly,
            direction
        )

        is_extreme = (
            anomaly.severity == "extreme"
        )

        return WeatherAnomalyClassification(
            variable=variable,

            category=category,

            direction=direction,

            severity=anomaly.severity,

            is_extreme=is_extreme
        )

    def _get_direction(
        self,
        anomaly
    ):
        """
        Determine whether the anomaly is positive,
        negative, or neutral.
        """

        if anomaly.absolute_anomaly > 0:
            return "positive"

        if anomaly.absolute_anomaly < 0:
            return "negative"

        return "neutral"

    def _get_category(
        self,
        anomaly,
        direction
    ):
        """
        Determine the weather anomaly category.
        """

        variable = anomaly.variable

        if variable == "temperature":

            if direction == "positive":
                return "extreme_heat"

            if direction == "negative":
                return "extreme_cold"

            return "temperature_anomaly"

        if variable == "dewpoint":

            if direction == "positive":
                return "high_moisture"

            if direction == "negative":
                return "low_moisture"

            return "dewpoint_anomaly"

        if variable == "wind_u":
            return "extreme_wind_u"

        if variable == "wind_v":
            return "extreme_wind_v"

        if variable == "wind_speed":
            return "extreme_wind"

        if variable == "total_precipitation":

            if direction == "positive":
                return "extreme_rainfall"

            if direction == "negative":
                return "rainfall_deficit"

            return "precipitation_anomaly"

        if variable == "mean_sea_level_pressure":

            if direction == "negative":
                return "low_pressure"

            if direction == "positive":
                return "high_pressure"

            return "pressure_anomaly"

        if variable == "surface_pressure":

            if direction == "negative":
                return "low_surface_pressure"

            if direction == "positive":
                return "high_surface_pressure"

            return "surface_pressure_anomaly"

        return "unknown"