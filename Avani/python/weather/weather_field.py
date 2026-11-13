
class WeatherField:
    """
    Represents a weather variable over a spatial grid
    at one point in time.

    The data may remain an xarray DataArray so consumers
    can perform lazy spatial selection before materializing it.
    """

    def __init__(
        self,
        variable,
        time,
        latitudes,
        longitudes,
        data,
        unit,
    ):
        self.variable = variable
        self.time = time

        self.latitudes = latitudes
        self.longitudes = longitudes

        # Preserve xarray objects and their lazy operations.
        self.data = data
        self.unit = unit

    @property
    def shape(self):
        """Return the spatial field shape."""
        return self.data.shape
