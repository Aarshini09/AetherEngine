from weather.weather_grid_node import WeatherGridNode


class WeatherDataIndex:
    """
    Spatial index for weather grid locations.

    The index creates a stable node identity for every
    latitude/longitude position in the selected weather grid.

    Weather values themselves are not stored here.
    """

    def __init__(self, grid_index):
        self.grid_index = grid_index

        self.nodes = {}
        self._coordinate_to_node = {}

    def build(
        self,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude
    ):
        """
        Build spatial nodes for an ERA5 geographic region.
        """

        self.nodes = {}
        self._coordinate_to_node = {}

        latitude_values = self.grid_index._latitudes
        longitude_values = self.grid_index._longitudes

        node_id = 0

        for latitude_index, latitude in enumerate(
            latitude_values
        ):

            if latitude < min_latitude:
                continue

            if latitude > max_latitude:
                continue

            for longitude_index, longitude in enumerate(
                longitude_values
            ):

                if longitude < min_longitude % 360.0:
                    continue

                if longitude > max_longitude % 360.0:
                    continue

                node = WeatherGridNode(
                    node_id=node_id,
                    latitude=latitude,
                    longitude=longitude,
                    latitude_index=latitude_index,
                    longitude_index=longitude_index
                )

                self.nodes[node_id] = node

                self._coordinate_to_node[
                    (
                        latitude_index,
                        longitude_index
                    )
                ] = node_id

                node_id += 1

        self._build_neighbors()

    def get_node(self, node_id):
        """
        Return a node by its ID.
        """

        if node_id not in self.nodes:
            raise KeyError(
                f"Weather grid node not found: {node_id}"
            )

        return self.nodes[node_id]

    def get_node_count(self):
        """
        Return the number of indexed spatial nodes.
        """

        return len(self.nodes)

    def get_node_at_indices(
        self,
        latitude_index,
        longitude_index
    ):
        """
        Return the node corresponding to an ERA5 grid index.
        """

        key = (
            latitude_index,
            longitude_index
        )

        if key not in self._coordinate_to_node:
            raise KeyError(
                "No weather grid node exists for "
                f"indices {key}."
            )

        node_id = self._coordinate_to_node[key]

        return self.nodes[node_id]

    def _build_neighbors(self):
        """
        Build immediate four-direction spatial
        grid relationships.

        Neighbors:
            north
            south
            east
            west
        """

        for node in self.nodes.values():

            latitude_index = node.latitude_index
            longitude_index = node.longitude_index

            neighbor_indices = [
                (
                    latitude_index - 1,
                    longitude_index
                ),
                (
                    latitude_index + 1,
                    longitude_index
                ),
                (
                    latitude_index,
                    longitude_index - 1
                ),
                (
                    latitude_index,
                    longitude_index + 1
                )
            ]

            for neighbor_index in neighbor_indices:

                neighbor_id = (
                    self._coordinate_to_node.get(
                        neighbor_index
                    )
                )

                if neighbor_id is not None:
                    node.add_neighbor(
                        neighbor_id
                    )