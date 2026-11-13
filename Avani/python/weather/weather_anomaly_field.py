class WeatherAnomalyField:
    """
    Represents weather anomalies across a spatial weather
    grid at one point in time.

    The field stores anomaly results associated with
    spatial weather-grid nodes.

    It does not determine whether observations are
    anomalous. That work is performed by AnomalyDetector.

    It also does not determine event regions. Spatial
    grouping will be handled by a later layer.
    """

    def __init__(
        self,
        time
    ):
        self.time = time

        self.anomalies = {}

        self.classifications = {}

    def add_anomaly(
        self,
        node_id,
        anomaly,
        classification
    ):
        """
        Add an anomaly and its classification to the field.
        """

        node_id = int(node_id)

        self.anomalies[node_id] = anomaly

        self.classifications[node_id] = classification

    def has_anomaly(
        self,
        node_id
    ):
        """
        Check whether a node contains a detected anomaly.
        """

        return int(node_id) in self.anomalies

    def get_anomaly(
        self,
        node_id
    ):
        """
        Return the anomaly associated with a node.
        """

        node_id = int(node_id)

        if node_id not in self.anomalies:
            raise KeyError(
                f"No anomaly exists for node: {node_id}"
            )

        return self.anomalies[node_id]

    def get_classification(
        self,
        node_id
    ):
        """
        Return the classification associated with a node.
        """

        node_id = int(node_id)

        if node_id not in self.classifications:
            raise KeyError(
                f"No classification exists for node: {node_id}"
            )

        return self.classifications[node_id]

    def get_anomalous_node_ids(self):
        """
        Return the IDs of all spatial nodes containing
        detected anomalies.
        """

        return list(
            self.anomalies.keys()
        )

    def get_anomaly_count(self):
        """
        Return the number of anomalous spatial nodes.
        """

        return len(
            self.anomalies
        )

    def get_nodes_by_category(
        self,
        category
    ):
        """
        Return node IDs belonging to a specific
        anomaly category.

        Example:

            extreme_heat
            extreme_cold
            low_pressure
        """

        return [
            node_id
            for node_id, classification
            in self.classifications.items()
            if classification.category == category
        ]

    def get_nodes_by_severity(
        self,
        severity
    ):
        """
        Return node IDs having a specific anomaly severity.
        """

        return [
            node_id
            for node_id, anomaly
            in self.anomalies.items()
            if anomaly.severity == severity
        ]

    def get_node_count_by_category(self):
        """
        Count anomalous nodes grouped by classification
        category.

        Returns:

            {
                "extreme_heat": 12,
                "extreme_cold": 4
            }
        """

        counts = {}

        for classification in self.classifications.values():

            category = classification.category

            counts[category] = (
                counts.get(category, 0)
                + 1
            )

        return counts

    def __len__(self):
        """
        Return the number of anomalous spatial nodes.
        """

        return self.get_anomaly_count()

    def __repr__(self):
        return (
            f"WeatherAnomalyField("
            f"time={self.time}, "
            f"anomaly_count="
            f"{self.get_anomaly_count()}"
            f")"
        )