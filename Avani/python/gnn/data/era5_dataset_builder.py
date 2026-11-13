
from datetime import datetime

from weather.weather_data_index import WeatherDataIndex
from weather.weather_data_graph_builder import WeatherDataGraphBuilder

from gnn.data.weather_graph_adapter import WeatherGraphAdapter


class ERA5DatasetBuilder:
    """
    Incrementally converts Avani's ERA5 weather data into
    graph examples suitable for TensorFlow GNN training.

    Each yielded example represents one timestamp and contains:
        - node_features: [N, F]
        - edge_index: [2, E]
        - metadata: timestamp, node IDs, feature names, and mappings

    This class prepares inputs only. It does not invent anomaly labels.
    """

    def __init__(self, weather_dataset, region):
        self.weather_dataset = weather_dataset
        self.region = region

        self.data_index = None
        self.graph_builder = None

    def initialize(self):
        """Build the spatial index for the selected region."""

        if self.data_index is not None:
            return

        self.data_index = WeatherDataIndex(
            self.weather_dataset.grid_index
        )

        self.data_index.build(**self.region)

        if self.data_index.get_node_count() == 0:
            raise ValueError(
                "The selected region contains no weather grid nodes."
            )

        self.graph_builder = WeatherDataGraphBuilder(
            weather_dataset=self.weather_dataset,
            data_index=self.data_index,
        )

    @property
    def node_count(self):
        """Number of spatial grid nodes in the selected region."""

        self.initialize()
        return self.data_index.get_node_count()

    def get_timestamps(
        self,
        start_time,
        end_time,
        interval_hours=6,
    ):
        """Return available timestamps from the existing ERA5 dataset."""

        return self.weather_dataset.get_available_times(
            start_time=start_time,
            end_time=end_time,
            interval_hours=interval_hours,
        )

    def iter_examples(
        self,
        start_time,
        end_time,
        interval_hours=6,
    ):
        """
        Yield one validated graph example per available timestamp.

        Graphs are built incrementally instead of being accumulated
        in memory. Missing or non-finite features raise an error in
        WeatherGraphAdapter rather than silently becoming training data.
        """

        self.initialize()

        timestamps = self.get_timestamps(
            start_time=start_time,
            end_time=end_time,
            interval_hours=interval_hours,
        )

        for timestamp_text in timestamps:
            timestamp = datetime.fromisoformat(timestamp_text)

            graph = self.graph_builder.build(
                times=[timestamp],
            )

            inputs, metadata = WeatherGraphAdapter.convert(
                graph,
                timestamp,
            )

            yield {
                "inputs": inputs,
                "metadata": metadata,
            }
