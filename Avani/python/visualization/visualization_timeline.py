class VisualizationTimeline:
    """
    Represents visualization-ready data across multiple
    points in time.

    Each frame is a VisualizationData object representing
    one timestamp.

    Tracks and events describe temporal behavior across
    those frames.
    """

    def __init__(
        self,
        variable,
        frames=None,
        tracks=None,
        events=None
    ):
        self.variable = variable

        self.frames = (
            []
            if frames is None
            else list(frames)
        )

        self.tracks = (
            []
            if tracks is None
            else list(tracks)
        )

        self.events = (
            []
            if events is None
            else list(events)
        )

    def add_frame(self, frame):
        if frame is None:
            raise ValueError(
                "Visualization frame cannot be None."
            )

        self.frames.append(frame)

    def add_track(self, track):
        if track is None:
            raise ValueError(
                "Visualization track cannot be None."
            )

        self.tracks.append(track)

    def add_event(self, event):
        if event is None:
            raise ValueError(
                "Visualization event cannot be None."
            )

        self.events.append(event)

    @property
    def frame_count(self):
        return len(self.frames)

    @property
    def start_time(self):
        if not self.frames:
            return None

        return self.frames[0].time

    @property
    def end_time(self):
        if not self.frames:
            return None

        return self.frames[-1].time

    def to_dict(self):
        return {
            "variable": self.variable,
            "start_time": _serialize_time(
                self.start_time
            ),
            "end_time": _serialize_time(
                self.end_time
            ),
            "frame_count": self.frame_count,
            "frames": [
                frame.to_dict()
                for frame in self.frames
            ],
            "tracks": self.tracks,
            "events": self.events
        }

    def __repr__(self):
        return (
            f"VisualizationTimeline("
            f"variable={self.variable}, "
            f"frames={self.frame_count}, "
            f"tracks={len(self.tracks)}, "
            f"events={len(self.events)}"
            f")"
        )


def _serialize_time(value):
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)