from weather.weather_coordinate import WeatherCoordinate


class WeatherGridNode:
    """
    Represents one spatial location in the weather grid.

    A WeatherGridNode identifies a geographic grid point.
    It does not contain the complete weather history.
    """

    def __init__(
        self,
        node_id,
        latitude,
        longitude,
        latitude_index,
        longitude_index
    ):
        self.node_id = int(node_id)

        self.coordinate = WeatherCoordinate(
            latitude=latitude,
            longitude=longitude
        )

        self.latitude_index = int(latitude_index)
        self.longitude_index = int(longitude_index)

        self.neighbors = []

    def add_neighbor(self, node_id):
        """
        Add another grid node as a spatial neighbor.
        """

        node_id = int(node_id)

        if node_id not in self.neighbors:
            self.neighbors.append(node_id)

    def __repr__(self):
        return (
            f"WeatherGridNode("
            f"node_id={self.node_id}, "
            f"latitude={self.coordinate.latitude}, "
            f"longitude={self.coordinate.longitude}, "
            f"latitude_index={self.latitude_index}, "
            f"longitude_index={self.longitude_index}"
            f")"
        )