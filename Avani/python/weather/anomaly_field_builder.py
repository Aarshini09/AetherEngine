from weather.weather_anomaly_field import (
    WeatherAnomalyField
)


class AnomalyFieldBuilder:
    def __init__(
        self,
        weather_dataset,
        data_index,
        baseline_processor,
        anomaly_detector,
        anomaly_classifier
    ):
        self.weather_dataset = weather_dataset
        self.data_index = data_index
        self.baseline_processor = baseline_processor
        self.anomaly_detector = anomaly_detector
        self.anomaly_classifier = anomaly_classifier

    def build(
        self,
        variable,
        time,
        baselines
    ):
        """
        Build an anomaly field for one timestamp.

        `baselines` must be indexed by node ID:

            {
                node_id: {
                    (month, hour): WeatherBaseline
                }
            }
        """

        anomaly_field = WeatherAnomalyField(
            time=time
        )

        baseline_key = self._get_baseline_key(
            time
        )

        for node_id, node in self.data_index.nodes.items():

            latitude = node.coordinate.latitude
            longitude = node.coordinate.longitude

            node_baselines = baselines.get(
                node_id
            )

            if node_baselines is None:
                continue

            if baseline_key not in node_baselines:
                continue

            baseline = node_baselines[
                baseline_key
            ]

            weather_value = (
                self.weather_dataset.get_value(
                    variable=variable,
                    time=time,
                    latitude=latitude,
                    longitude=longitude
                )
            )

            anomaly = (
                self.anomaly_detector.detect(
                    variable=variable,
                    time=time,
                    latitude=latitude,
                    longitude=longitude,
                    value=weather_value.value,
                    baseline=baseline
                )
            )

            if not anomaly.is_anomaly:
                continue

            classification = (
                self.anomaly_classifier.classify(
                    anomaly
                )
            )

            anomaly_field.add_anomaly(
                node_id=node_id,
                anomaly=anomaly,
                classification=classification
            )

        return anomaly_field

    def _get_baseline_key(self, time):

        timestamp = time

        if not hasattr(timestamp, "month"):

            import numpy as np

            timestamp = np.datetime64(
                timestamp
            )

            month = (
                timestamp.astype(
                    "datetime64[M]"
                ).astype(int) % 12
            ) + 1

            day_start = timestamp.astype(
                "datetime64[D]"
            )

            hour = int(
                (
                    timestamp - day_start
                ) / np.timedelta64(
                    1,
                    "h"
                )
            )

            return int(month), hour

        return (
            timestamp.month,
            timestamp.hour
        )