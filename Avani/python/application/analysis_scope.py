class AnalysisScope:
    """
    Defines the geographic and temporal scope of an Avani
    analysis request.

    The scope does not perform analysis.

    It only describes what part of the weather dataset
    the analysis system should operate on.
    """

    def __init__(
        self,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
        variable,
        start_time=None,
        end_time=None
    ):
        self.min_latitude = float(min_latitude)
        self.max_latitude = float(max_latitude)

        self.min_longitude = float(min_longitude)
        self.max_longitude = float(max_longitude)

        self.variable = variable

        self.start_time = start_time
        self.end_time = end_time

        self._validate()

    def _validate(self):
        if self.min_latitude > self.max_latitude:
            raise ValueError(
                "Minimum latitude cannot be greater than "
                "maximum latitude."
            )

        if self.min_longitude > self.max_longitude:
            raise ValueError(
                "Minimum longitude cannot be greater than "
                "maximum longitude."
            )

        if not self.variable:
            raise ValueError(
                "An analysis variable is required."
            )

    @property
    def latitude_span(self):
        return (
            self.max_latitude -
            self.min_latitude
        )

    @property
    def longitude_span(self):
        return (
            self.max_longitude -
            self.min_longitude
        )

    def __repr__(self):
        return (
            "AnalysisScope("
            f"latitude=({self.min_latitude}, "
            f"{self.max_latitude}), "
            f"longitude=({self.min_longitude}, "
            f"{self.max_longitude}), "
            f"variable='{self.variable}', "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time}"
            ")"
        )