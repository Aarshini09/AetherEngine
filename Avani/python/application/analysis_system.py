from weather.anomaly_detector import AnomalyDetector
from weather.anomaly_classifier import AnomalyClassifier
from weather.anomaly_field_builder import AnomalyFieldBuilder
from weather.anomaly_region_builder import AnomalyRegionBuilder
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker
from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor
)
from weather.weather_event import WeatherEvent


class AnalysisSystem:
    """
    Application-level owner of the Avani weather-analysis pipeline.

    The AnalysisSystem coordinates the existing weather-analysis
    components but does not replace their domain responsibilities.

    Pipeline:

        Historical Baseline
              ↓
        Anomaly Detection
              ↓
        Classification
              ↓
        Anomaly Field
              ↓
        Spatial Regions
              ↓
        Temporal Tracks
              ↓
        Weather Events

    The system is request-driven.

    Expensive historical analysis is not performed automatically
    on every application runtime tick.
    """

    def __init__(
        self,
        weather_bridge,
        weather_dataset,
        data_index,
        anomaly_threshold=2.0,
        maximum_latitude_distance=1.0,
        maximum_longitude_distance=1.0
    ):
        self.weather_bridge = weather_bridge
        self.weather_dataset = weather_dataset
        self.data_index = data_index

        self.anomaly_detector = AnomalyDetector(
            threshold=anomaly_threshold
        )

        self.anomaly_classifier = AnomalyClassifier()

        self.anomaly_field_builder = AnomalyFieldBuilder(
            weather_dataset=self.weather_dataset,
            data_index=self.data_index,
            baseline_processor=None,
            anomaly_detector=self.anomaly_detector,
            anomaly_classifier=self.anomaly_classifier
        )

        self.anomaly_region_builder = AnomalyRegionBuilder(
            data_index=self.data_index
        )

        self.anomaly_temporal_tracker = (
            AnomalyTemporalTracker(
                maximum_latitude_distance=(
                    maximum_latitude_distance
                ),
                maximum_longitude_distance=(
                    maximum_longitude_distance
                )
            )
        )

        self._initialized = False

        self._anomaly_fields = []
        self._region_fields = []
        self._tracks = []
        self._events = []

    def initialize(self):
        """
        Initialize the analysis system.
        """

        if self._initialized:
            raise RuntimeError(
                "AnalysisSystem is already initialized."
            )

        self._clear_results()

        self._initialized = True

        print("[Analysis] Analysis system ready.")

    def shutdown(self):
        """
        Shut down the analysis system.
        """

        if not self._initialized:
            return

        self._clear_results()

        self._initialized = False

        print("[Analysis] Analysis system shutdown.")

    def build_baselines(
        self,
        variable,
        start_time=None,
        end_time=None
    ):
        """
        Build a historical baseline for every spatial node
        currently contained in the WeatherDataIndex.

        Returns:

            {
                node_id: {
                    (month, hour): WeatherBaseline
                }
            }
        """

        self._require_initialized()

        reader = self.weather_bridge.get_reader(
            variable
        )

        processor = HistoricalBaselineProcessor(
            reader
        )

        baselines_by_node = {}

        for node_id, node in self.data_index.nodes.items():

            baselines = processor.compute_point_baseline(
                variable_name=variable,
                latitude=node.coordinate.latitude,
                longitude=node.coordinate.longitude,
                start_time=start_time,
                end_time=end_time
            )

            baselines_by_node[node_id] = baselines

        return baselines_by_node

    def analyze_time(
        self,
        variable,
        time,
        baselines_by_node
    ):
        """
        Analyze one timestamp.

        Baselines are supplied separately for each spatial node.
        """

        self._require_initialized()

        anomaly_field = (
            self.anomaly_field_builder.build(
                variable=variable,
                time=time,
                baselines=baselines_by_node
            )
        )

        regions = (
            self.anomaly_region_builder.build(
                anomaly_field
            )
        )

        result = {
            "time": time,
            "variable": variable,
            "anomaly_field": anomaly_field,
            "regions": regions
        }

        self._anomaly_fields.append(
            anomaly_field
        )

        self._region_fields.append(
            {
                "time": time,
                "regions": regions
            }
        )

        return result

    def analyze_time_range(
        self,
        variable,
        times,
        baselines_by_node
    ):
        """
        Analyze multiple timestamps and construct
        temporal tracks and weather events.
        """

        self._require_initialized()

        self._clear_results()

        for time in times:

            self.analyze_time(
                variable=variable,
                time=time,
                baselines_by_node=baselines_by_node
            )

        self._tracks = (
            self.anomaly_temporal_tracker.build_tracks(
                self._region_fields
            )
        )

        self._events = (
            self._build_events(
                self._tracks
            )
        )

        return {
            "variable": variable,
            "fields": list(
                self._anomaly_fields
            ),
            "region_fields": list(
                self._region_fields
            ),
            "tracks": list(
                self._tracks
            ),
            "events": list(
                self._events
            )
        }

    def _build_events(self, tracks):
        """
        Convert anomaly tracks into application-level events.
        """

        events = []

        for event_id, track in enumerate(tracks):

            event = WeatherEvent(
                event_id=event_id,
                category=track.category,
                track=track
            )

            events.append(event)

        return events

    def get_anomaly_fields(self):
        return list(
            self._anomaly_fields
        )

    def get_region_fields(self):
        return list(
            self._region_fields
        )

    def get_tracks(self):
        return list(
            self._tracks
        )

    def get_events(self):
        return list(
            self._events
        )

    def clear_results(self):
        self._require_initialized()
        self._clear_results()

    def _clear_results(self):
        self._anomaly_fields.clear()
        self._region_fields.clear()
        self._tracks.clear()
        self._events.clear()

    def _require_initialized(self):
        if not self._initialized:
            raise RuntimeError(
                "AnalysisSystem must be initialized before "
                "performing analysis."
            )

    @property
    def initialized(self):
        return self._initialized

    @property
    def anomaly_field_count(self):
        return len(
            self._anomaly_fields
        )

    @property
    def region_field_count(self):
        return len(
            self._region_fields
        )

    @property
    def track_count(self):
        return len(
            self._tracks
        )

    @property
    def event_count(self):
        return len(
            self._events
        )
from weather.anomaly_detector import AnomalyDetector
from weather.anomaly_classifier import AnomalyClassifier
from weather.anomaly_field_builder import AnomalyFieldBuilder
from weather.anomaly_region_builder import AnomalyRegionBuilder
from weather.anomaly_temporal_tracker import AnomalyTemporalTracker
from weather.historical_baseline_processor import (
    HistoricalBaselineProcessor,
)
from weather.weather_event import WeatherEvent


class AnalysisSystem:
    """
    Application-level owner of the Avani weather-analysis pipeline.

    Coordinates the existing analysis components without replacing
    their domain responsibilities.

    Pipeline:
        Historical Baseline
              |
        Anomaly Detection
              |
        Classification
              |
        Anomaly Field
              |
        Spatial Regions
              |
        Temporal Tracks
              |
        Weather Events

    Historical analysis is request-driven rather than being performed
    automatically on every application runtime tick.
    """

    def __init__(
        self,
        weather_bridge,
        weather_dataset,
        data_index,
        anomaly_threshold=2.0,
        maximum_distance_km=300.0,
        expected_interval_hours=6.0,
        max_missed_observations=1,
        maximum_shape_distance_km=150.0,
        intensity_weight_km=50.0,
    ):
        self.weather_bridge = weather_bridge
        self.weather_dataset = weather_dataset
        self.data_index = data_index

        self.anomaly_detector = AnomalyDetector(
            threshold=anomaly_threshold,
        )

        self.anomaly_classifier = AnomalyClassifier()

        self.anomaly_field_builder = AnomalyFieldBuilder(
            weather_dataset=self.weather_dataset,
            data_index=self.data_index,
            baseline_processor=None,
            anomaly_detector=self.anomaly_detector,
            anomaly_classifier=self.anomaly_classifier,
        )

        self.anomaly_region_builder = AnomalyRegionBuilder(
            data_index=self.data_index,
        )

        self.anomaly_temporal_tracker = AnomalyTemporalTracker(
            maximum_distance_km=maximum_distance_km,
            expected_interval_hours=expected_interval_hours,
            max_missed_observations=max_missed_observations,
            maximum_shape_distance_km=maximum_shape_distance_km,
            intensity_weight_km=intensity_weight_km,
        )

        self._initialized = False

        self._anomaly_fields = []
        self._region_fields = []
        self._tracks = []
        self._events = []

    def initialize(self):
        """Initialize the analysis system."""

        if self._initialized:
            raise RuntimeError(
                "AnalysisSystem is already initialized."
            )

        self._clear_results()
        self._initialized = True

        print("[Analysis] Analysis system ready.")

    def shutdown(self):
        """Shut down the analysis system."""

        if not self._initialized:
            return

        self._clear_results()
        self._initialized = False

        print("[Analysis] Analysis system shutdown.")

    def build_baselines(
        self,
        variable,
        start_time=None,
        end_time=None,
    ):
        """
        Build a historical baseline for each spatial node.

        Returns:
            {
                node_id: {
                    (month, hour): WeatherBaseline
                }
            }
        """

        self._require_initialized()

        reader = self.weather_bridge.get_reader(variable)

        processor = HistoricalBaselineProcessor(reader)

        baselines_by_node = {}

        for node_id, node in self.data_index.nodes.items():
            baselines = processor.compute_point_baseline(
                variable_name=variable,
                latitude=node.coordinate.latitude,
                longitude=node.coordinate.longitude,
                start_time=start_time,
                end_time=end_time,
            )

            baselines_by_node[node_id] = baselines

        return baselines_by_node

    def analyze_time(
        self,
        variable,
        time,
        baselines_by_node,
    ):
        """Analyze anomalies and spatial regions for one timestamp."""

        self._require_initialized()

        anomaly_field = self.anomaly_field_builder.build(
            variable=variable,
            time=time,
            baselines=baselines_by_node,
        )

        regions = self.anomaly_region_builder.build(
            anomaly_field,
        )

        result = {
            "time": time,
            "variable": variable,
            "anomaly_field": anomaly_field,
            "regions": regions,
        }

        self._anomaly_fields.append(anomaly_field)

        self._region_fields.append(
            {
                "time": time,
                "regions": regions,
            }
        )

        return result

    def analyze_time_range(
        self,
        variable,
        times,
        baselines_by_node,
    ):
        """
        Analyze multiple timestamps, then construct temporal tracks
        and weather events from the resulting regions.
        """

        self._require_initialized()

        self._clear_results()

        for time in times:
            self.analyze_time(
                variable=variable,
                time=time,
                baselines_by_node=baselines_by_node,
            )

        self._tracks = (
            self.anomaly_temporal_tracker.build_tracks(
                self._region_fields,
            )
        )

        self._events = self._build_events(self._tracks)

        return {
            "variable": variable,
            "fields": list(self._anomaly_fields),
            "region_fields": list(self._region_fields),
            "tracks": list(self._tracks),
            "events": list(self._events),
        }

    def _build_events(self, tracks):
        """Convert anomaly tracks into application-level events."""

        events = []

        for event_id, track in enumerate(tracks):
            event = WeatherEvent(
                event_id=event_id,
                category=track.category,
                track=track,
            )

            events.append(event)

        return events

    def get_anomaly_fields(self):
        return list(self._anomaly_fields)

    def get_region_fields(self):
        return list(self._region_fields)

    def get_tracks(self):
        return list(self._tracks)

    def get_events(self):
        return list(self._events)

    def clear_results(self):
        """Clear stored analysis results."""

        self._require_initialized()
        self._clear_results()

    def _clear_results(self):
        """Clear internal result collections."""

        self._anomaly_fields.clear()
        self._region_fields.clear()
        self._tracks.clear()
        self._events.clear()

    def _require_initialized(self):
        if not self._initialized:
            raise RuntimeError(
                "AnalysisSystem must be initialized before "
                "performing analysis."
            )

    @property
    def initialized(self):
        return self._initialized

    @property
    def anomaly_field_count(self):
        return len(self._anomaly_fields)

    @property
    def region_field_count(self):
        return len(self._region_fields)

    @property
    def track_count(self):
        return len(self._tracks)

    @property
    def event_count(self):
        return len(self._events)
