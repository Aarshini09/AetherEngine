class WeatherEvent:
    """
    Represents a higher-level weather event derived from
    an anomaly track.

    A WeatherEvent provides an application-level
    representation of an evolving weather anomaly.

    The event stores descriptive information derived from
    its underlying anomaly track.

    It does not itself perform anomaly detection,
    spatial grouping, temporal tracking, or threat
    assessment.
    """

    def __init__(
        self,
        event_id,
        category,
        track
    ):
        self.event_id = int(event_id)

        self.category = category

        self.track = track

        self.start_time = track.start_time
        self.end_time = track.end_time

        self.region_count = track.region_count

        self.start_latitude = None
        self.start_longitude = None

        self.end_latitude = None
        self.end_longitude = None

        self.minimum_value = None
        self.maximum_value = None

        self.minimum_standardized_anomaly = None
        self.maximum_standardized_anomaly = None

        self.threat_level = "unknown"

        self._initialize_from_track()

    def _initialize_from_track(self):
        """
        Initialize event-level information from the
        underlying anomaly track.
        """

        if not self.track.regions:
            return

        first_region = self.track.regions[0]
        last_region = self.track.regions[-1]

        self.start_latitude = (
            first_region.min_latitude +
            first_region.max_latitude
        ) / 2.0

        self.start_longitude = (
            first_region.min_longitude +
            first_region.max_longitude
        ) / 2.0

        self.end_latitude = (
            last_region.min_latitude +
            last_region.max_latitude
        ) / 2.0

        self.end_longitude = (
            last_region.min_longitude +
            last_region.max_longitude
        ) / 2.0

        values = []

        standardized_anomalies = []

        for region in self.track.regions:

            if region.min_value is not None:
                values.append(region.min_value)

            if region.max_value is not None:
                values.append(region.max_value)

            if region.min_standardized_anomaly is not None:
                standardized_anomalies.append(
                    region.min_standardized_anomaly
                )

            if region.max_standardized_anomaly is not None:
                standardized_anomalies.append(
                    region.max_standardized_anomaly
                )

        if values:
            self.minimum_value = min(values)
            self.maximum_value = max(values)

        if standardized_anomalies:
            self.minimum_standardized_anomaly = min(
                standardized_anomalies
            )

            self.maximum_standardized_anomaly = max(
                standardized_anomalies
            )

    @property
    def duration_steps(self):
        """
        Return the number of temporal observations
        represented by the event.
        """

        return self.region_count

    @property
    def start_location(self):
        """
        Return the geographic starting location.
        """

        return (
            self.start_latitude,
            self.start_longitude
        )

    @property
    def end_location(self):
        """
        Return the geographic ending location.
        """

        return (
            self.end_latitude,
            self.end_longitude
        )

    @property
    def has_movement(self):
        """
        Determine whether the event's start and end
        geographic positions differ.
        """

        if (
            self.start_latitude is None
            or self.start_longitude is None
            or self.end_latitude is None
            or self.end_longitude is None
        ):
            return False

        return (
            self.start_latitude != self.end_latitude
            or
            self.start_longitude != self.end_longitude
        )

    def __repr__(self):
        return (
            f"WeatherEvent("
            f"event_id={self.event_id}, "
            f"category={self.category}, "
            f"region_count={self.region_count}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time}, "
            f"threat_level={self.threat_level}"
            f")"
        )