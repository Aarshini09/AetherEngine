class WeatherAnomalyClassification:
    """
    Represents the classification of a detected
    weather anomaly.

    The classification describes what type of weather
    anomaly was detected.

    Examples:

        extreme_heat
        extreme_cold
        extreme_wind
        extreme_rainfall
        low_pressure
        high_pressure
    """

    def __init__(
        self,
        variable,
        category,
        direction,
        severity,
        is_extreme
    ):
        self.variable = variable
        self.category = category
        self.direction = direction
        self.severity = severity
        self.is_extreme = bool(
            is_extreme
        )

    def __repr__(self):
        return (
            f"WeatherAnomalyClassification("
            f"variable={self.variable}, "
            f"category={self.category}, "
            f"direction={self.direction}, "
            f"severity={self.severity}, "
            f"is_extreme={self.is_extreme}"
            f")"
        )