from weather.weather_data_graph import WeatherDataGraph


class WeatherDataGraphBuilder:
    """
    Builds a spatio-temporal WeatherDataGraph from
    a WeatherDataset and WeatherDataIndex.

    The builder connects:

        spatial node
            +
        timestamp
            +
        WeatherState

    and then constructs temporal relationships
    between consecutive timestamps.
    """

    def __init__(
        self,
        weather_dataset,
        data_index
    ):
        self.weather_dataset = weather_dataset
        self.data_index = data_index

    def build(
        self,
        times
    ):
        """
        Build the weather data graph for the requested
        timestamps.

        Returns:
            WeatherDataGraph
        """

        graph = WeatherDataGraph(
            self.data_index
        )

        graph.initialize()

        for node_id, node in self.data_index.nodes.items():

            for time in times:

                state = self.weather_dataset.get_state(
                    time=time,
                    latitude=node.coordinate.latitude,
                    longitude=node.coordinate.longitude
                )

                graph.add_state(
                    node_id=node_id,
                    time=time,
                    state=state
                )

        # Once all states have been inserted,
        # connect consecutive timestamps.
        graph.build_temporal_edges()

        return graph