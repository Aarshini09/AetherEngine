class VisualizationData:
    """
    Visualization-ready representation of weather data
    and analysis results for one timestamp.

    This object forms the boundary between the Python
    analysis system and the frontend visualization system.
    """

    def __init__(
        self,
        time,
        variable,
        values=None,
        anomalies=None,
        regions=None,
        tracks=None,
        events=None
    ):
        self.time = time
        self.variable = variable

        self.values = (
            [] if values is None
            else list(values)
        )

        self.anomalies = (
            [] if anomalies is None
            else list(anomalies)
        )

        self.regions = (
            [] if regions is None
            else list(regions)
        )

        self.tracks = (
            [] if tracks is None
            else list(tracks)
        )

        self.events = (
            [] if events is None
            else list(events)
        )

    def to_dict(self):
        return {
            "time": _serialize_time(self.time),
            "variable": self.variable,
            "values": self.values,
            "anomalies": self.anomalies,
            "regions": self.regions,
            "tracks": self.tracks,
            "events": self.events
        }

    def __repr__(self):
        return (
            "VisualizationData("
            f"time={self.time!r}, "
            f"variable={self.variable!r}, "
            f"values={len(self.values)}, "
            f"anomalies={len(self.anomalies)}, "
            f"regions={len(self.regions)}, "
            f"tracks={len(self.tracks)}, "
            f"events={len(self.events)}"
            ")"
        )


def _serialize_time(value):
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)