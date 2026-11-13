from weather.weather_anomaly_region import (
    WeatherAnomalyRegion
)


class AnomalyRegionBuilder:
    """
    Extracts spatially connected anomaly regions from
    a WeatherAnomalyField.

    Spatial connectivity is determined using the neighbor
    relationships stored in WeatherDataIndex.

    The builder uses connected-component traversal and
    does not assume that an anomaly region is rectangular.
    """

    def __init__(
        self,
        data_index
    ):
        self.data_index = data_index

    def build(
        self,
        anomaly_field
    ):
        """
        Build spatial anomaly regions.

        Returns:

            [
                WeatherAnomalyRegion,
                ...
            ]
        """

        regions = []

        visited = set()

        region_id = 0

        anomalous_nodes = set(
            anomaly_field.get_anomalous_node_ids()
        )

        for node_id in anomalous_nodes:

            if node_id in visited:
                continue

            region_nodes = (
                self._find_connected_component(
                    node_id=node_id,
                    anomalous_nodes=anomalous_nodes,
                    visited=visited
                )
            )

            if not region_nodes:
                continue

            category = (
                anomaly_field.get_classification(
                    region_nodes[0]
                ).category
            )

            region = WeatherAnomalyRegion(
                region_id=region_id,

                time=anomaly_field.time,

                category=category
            )

            for region_node_id in region_nodes:

                node = self.data_index.get_node(
                    region_node_id
                )

                anomaly = (
                    anomaly_field.get_anomaly(
                        region_node_id
                    )
                )

                region.add_node(
                    node_id=region_node_id,

                    latitude=(
                        node.coordinate.latitude
                    ),

                    longitude=(
                        node.coordinate.longitude
                    ),

                    value=anomaly.value,

                    standardized_anomaly=(
                        anomaly.standardized_anomaly
                    )
                )

            regions.append(
                region
            )

            region_id += 1

        return regions

    def _find_connected_component(
        self,
        node_id,
        anomalous_nodes,
        visited
    ):
        """
        Find one connected anomalous component using
        depth-first traversal.
        """

        component = []

        stack = [
            node_id
        ]

        visited.add(
            node_id
        )

        while stack:

            current_node_id = stack.pop()

            component.append(
                current_node_id
            )

            node = self.data_index.get_node(
                current_node_id
            )

            for neighbor_id in node.neighbors:

                if neighbor_id not in anomalous_nodes:
                    continue

                if neighbor_id in visited:
                    continue

                visited.add(
                    neighbor_id
                )

                stack.append(
                    neighbor_id
                )

        return component