class WeatherCoordinate:
    """
    Represents the authoritative geographic location of
    a weather observation.

    Latitude and longitude define the horizontal geographic
    position.

    Height represents the vertical position/elevation when
    that information is available.

    The coordinate is the authoritative geographic identity.
    Spatial representations such as grid indices or
    icosahedral cells must not replace it.
    """

    def __init__(
        self,
        latitude,
        longitude,
        height=None
    ):
        self.latitude = float(latitude)
        self.longitude = float(longitude)

        self.height = (
            None
            if height is None
            else float(height)
        )

    def __repr__(self):
        return (
            f"WeatherCoordinate("
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"height={self.height}"
            f")"
        )