from weather.weather_node_series import WeatherNodeSeries


class WeatherDataGraph:
    """
    Represents the spatio-temporal weather data graph.

    The graph combines three kinds of information:

        1. Spatial topology
           Which weather nodes are spatial neighbors.

        2. Temporal topology
           How a node progresses from one timestamp
           to the next.

        3. Weather states
           The actual atmospheric state associated
           with each node and timestamp.
    """

    def __init__(self, data_index):
        self.data_index = data_index

        self.node_series = {}

        self.temporal_edges = {}

    def initialize(self):
        """
        Initialize graph storage for all spatial nodes.
        """

        self.node_series = {}
        self.temporal_edges = {}

        for node_id, node in self.data_index.nodes.items():

            self.node_series[node_id] = WeatherNodeSeries(
                node
            )

            self.temporal_edges[node_id] = {}

    # ---------------------------------------------------------
    # Node queries
    # ---------------------------------------------------------

    def get_node(self, node_id):
        """
        Return a spatial weather node by ID.
        """

        return self.data_index.get_node(
            node_id
        )

    def get_node_count(self):
        """
        Return the number of spatial nodes.
        """

        return self.data_index.get_node_count()

    # ---------------------------------------------------------
    # Spatial queries
    # ---------------------------------------------------------

    def get_spatial_neighbors(self, node_id):
        """
        Return the spatial neighbors of a node.
        """

        node = self.get_node(
            node_id
        )

        return [
            self.get_node(neighbor_id)
            for neighbor_id in node.neighbors
        ]

    def get_spatial_neighbor_ids(self, node_id):
        """
        Return the IDs of the spatial neighbors
        of a node.
        """

        node = self.get_node(
            node_id
        )

        return list(node.neighbors)

    # ---------------------------------------------------------
    # Weather state queries
    # ---------------------------------------------------------

    def add_state(
        self,
        node_id,
        time,
        state
    ):
        """
        Add a weather state to a spatial node.
        """

        if node_id not in self.node_series:
            raise KeyError(
                f"Weather node not found: {node_id}"
            )

        self.node_series[node_id].add_state(
            time=time,
            state=state
        )

    def get_node_series(self, node_id):
        """
        Return the complete temporal weather series
        for one spatial node.
        """

        if node_id not in self.node_series:
            raise KeyError(
                f"Weather node not found: {node_id}"
            )

        return self.node_series[node_id]

    def get_state(
        self,
        node_id,
        time
    ):
        """
        Return the weather state for a node at
        a specific timestamp.
        """

        series = self.get_node_series(
            node_id
        )

        return series.get_state(
            time
        )

    def get_state_count(self):
        """
        Return the total number of weather states
        currently stored in the graph.
        """

        return sum(
            len(series)
            for series in self.node_series.values()
        )

    # ---------------------------------------------------------
    # Temporal topology
    # ---------------------------------------------------------

    def build_temporal_edges(self):
        """
        Build temporal edges between consecutive
        timestamps for every spatial node.

        Example:

            Node 0 @ t0 → Node 0 @ t1
            Node 0 @ t1 → Node 0 @ t2
            Node 0 @ t2 → Node 0 @ t3
        """

        for node_id, series in self.node_series.items():

            times = sorted(
                series.get_times()
            )

            self.temporal_edges[node_id] = {}

            for index in range(
                len(times) - 1
            ):

                current_time = times[index]
                next_time = times[index + 1]

                self.temporal_edges[node_id][
                    current_time
                ] = next_time

    def get_next_time(
        self,
        node_id,
        time
    ):
        """
        Return the timestamp reached by following
        the next temporal edge.
        """

        if node_id not in self.temporal_edges:
            raise KeyError(
                f"Weather node not found: {node_id}"
            )

        return self.temporal_edges[
            node_id
        ].get(time)

    def get_temporal_edges(self, node_id):
        """
        Return all temporal edges for a node.

        The result maps:

            current_time → next_time
        """

        if node_id not in self.temporal_edges:
            raise KeyError(
                f"Weather node not found: {node_id}"
            )

        return dict(
            self.temporal_edges[node_id]
        )

    def get_temporal_edge_count(self):
        """
        Return the total number of temporal edges.
        """

        return sum(
            len(edges)
            for edges in self.temporal_edges.values()
        )

    # ---------------------------------------------------------
    # Combined graph queries
    # ---------------------------------------------------------

    def get_connected_node_ids(
        self,
        node_id
    ):
        """
        Return spatial node IDs connected to the
        requested node.

        Temporal relationships are intentionally
        excluded from this method because temporal
        connections do not lead to a different
        spatial node.
        """

        return self.get_spatial_neighbor_ids(
            node_id
        )

    def get_connected_state(
        self,
        node_id,
        time
    ):
        """
        Return the current state and the next temporal
        state for a node.

        Returns None for next_state when the requested
        timestamp is the final timestamp.
        """

        current_state = self.get_state(
            node_id,
            time
        )

        next_time = self.get_next_time(
            node_id,
            time
        )

        next_state = None

        if next_time is not None:

            next_state = self.get_state(
                node_id,
                next_time
            )

        return {
            "current_time": time,
            "current_state": current_state,
            "next_time": next_time,
            "next_state": next_state
        }