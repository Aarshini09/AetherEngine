# from application.analysis_scope import AnalysisScope
# from application.analysis_system import AnalysisSystem

# from weather.weather_data_bridge import WeatherDataBridge
# from weather.weather_dataset import WeatherDataset
# from weather.weather_data_index import WeatherDataIndex
# from weather.weather_data_graph_builder import (
#     WeatherDataGraphBuilder
# )
# from visualization.visualization_serializer import (
#     VisualizationSerializer
# )
# from application.weather_frame_service import WeatherFrameService

# class AvaniApplication:
#     """
#     Main application object for Avani.

#     AvaniApplication owns the lifetime of the major backend systems.

#     Individual weather, anomaly, tracking, event, and AI classes
#     remain responsible for their own domain logic.

#     This class is responsible for orchestration and application
#     lifecycle.
#     """

#     def __init__(self, weather_data_root):
#         self.weather_data_root = weather_data_root

#         self.weather_bridge = None
#         self.weather_dataset = None
#         self.weather_frame_service = None

#         self.weather_data_index = None
#         self.weather_data_graph = None
#         self.analysis_system = None

#         self.visualization_serializer = (
#             VisualizationSerializer()
#         )

#         self.analysis_scope = None

#         self._initialized = False
#         self._should_close = False

#         self.elapsed_time = 0.0
#         self.frame_count = 0

#     def initialize(self):
#         """
#         Initialize the Avani backend.
#         """

#         if self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication is already initialized."
#             )

#         print("========================================")
#         print("           AVANI APPLICATION")
#         print("========================================")
#         print()
#         print("[Avani] Initializing application...")
#         print()

#         self._initialize_weather_system()
#         self.weather_frame_service = WeatherFrameService(
#             self.weather_dataset
#         )

#         self._initialized = True

#         print()
#         print("[Avani] Application initialized.")
#         print("[Avani] Runtime ready.")
#         print()

#     def _initialize_weather_system(self):
#         print("[Weather] Initializing weather data system...")

#         self.weather_bridge = WeatherDataBridge(
#             self.weather_data_root
#         )

#         self.weather_dataset = WeatherDataset(
#             self.weather_bridge
#         )

#         print(
#             f"[Weather] Data root: "
#             f"{self.weather_data_root}"
#         )

#         print("[Weather] Opening ERA5 dataset...")

#         self.weather_dataset.open()

#         print("[Weather] ERA5 dataset opened.")
#         print("[Weather] Weather data system ready.")

    
#     def get_temperature_frame(
#         self,
#         time,
#         min_latitude=-90.0,
#         max_latitude=90.0,
#         min_longitude=-180.0,
#         max_longitude=180.0,
#         max_rows=91,
#         max_columns=180,
#     ):
#         """
#         Return a visualization-ready temperature frame
#         for the requested time and geographic region.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.weather_frame_service is None:
#             raise RuntimeError(
#                 "WeatherFrameService is not initialized."
#             )

#         return self.weather_frame_service.get_temperature_frame(
#             time=time,
#             min_latitude=min_latitude,
#             max_latitude=max_latitude,
#             min_longitude=min_longitude,
#             max_longitude=max_longitude,
#             max_rows=max_rows,
#             max_columns=max_columns,
#         )


#     def get_weather_frame(
#         self,
#         variable,
#         time,
#         min_latitude=-90.0,
#         max_latitude=90.0,
#         min_longitude=-180.0,
#         max_longitude=180.0,
#         max_rows=91,
#         max_columns=180,
#     ):
#         """
#         Request a sampled weather field directly from the
#         persistent weather dataset.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.weather_frame_service is None:
#             raise RuntimeError(
#                 "WeatherFrameService is not initialized."
#             )

#         return self.weather_frame_service.get_weather_frame(
#             variable=variable,
#             time=time,
#             min_latitude=min_latitude,
#             max_latitude=max_latitude,
#             min_longitude=min_longitude,
#             max_longitude=max_longitude,
#             max_rows=max_rows,
#             max_columns=max_columns,
#         )


#     def configure_analysis(self, scope):
#         """
#         Configure the geographic analysis world.

#         This creates the spatial WeatherDataIndex and
#         AnalysisSystem for the supplied analysis scope.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized "
#                 "before configuring analysis."
#             )

#         if not isinstance(
#             scope,
#             AnalysisScope
#         ):
#             raise TypeError(
#                 "scope must be an AnalysisScope."
#             )

#         if self.analysis_system is not None:
#             raise RuntimeError(
#                 "Analysis has already been configured."
#             )

#         self.analysis_scope = scope

#         print(
#             "[Analysis] Configuring analysis scope..."
#         )

#         print(
#             f"[Analysis] Variable: "
#             f"{scope.variable}"
#         )

#         print(
#             "[Analysis] Latitude: "
#             f"{scope.min_latitude} → "
#             f"{scope.max_latitude}"
#         )

#         print(
#             "[Analysis] Longitude: "
#             f"{scope.min_longitude} → "
#             f"{scope.max_longitude}"
#         )

#         self.weather_data_index = WeatherDataIndex(
#             self.weather_dataset.grid_index
#         )

#         self.weather_data_index.build(
#             min_latitude=scope.min_latitude,
#             max_latitude=scope.max_latitude,
#             min_longitude=scope.min_longitude,
#             max_longitude=scope.max_longitude
#         )

#         print(
#             "[Analysis] Spatial index created."
#         )

#         print(
#             f"[Analysis] Spatial nodes: "
#             f"{self.weather_data_index.get_node_count()}"
#         )

#         self.analysis_system = AnalysisSystem(
#             weather_bridge=self.weather_bridge,
#             weather_dataset=self.weather_dataset,
#             data_index=self.weather_data_index
#         )

#         self.analysis_system.initialize()

#         print(
#             "[Analysis] Analysis system configured."
#         )
#         print()

#     def run_analysis(self, time):
#         """
#         Run a complete analysis for one timestamp.

#         This performs:

#             Baseline
#             Anomaly Detection
#             Classification
#             Anomaly Field
#             Spatial Regions

#         Temporal tracking and event generation require
#         multiple timestamps and are handled by
#         run_analysis_range().
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.analysis_system is None:
#             raise RuntimeError(
#                 "Analysis system has not been configured."
#             )

#         variable = self.analysis_scope.variable

#         print("========================================")
#         print("          AVANI ANALYSIS")
#         print("========================================")
#         print()

#         print(
#             f"[Analysis] Variable: {variable}"
#         )

#         print(
#             f"[Analysis] Time: {time}"
#         )

#         print(
#             "[Analysis] Building historical baselines..."
#         )

#         baselines = (
#             self.analysis_system.build_baselines(
#                 variable=variable,
#                 start_time=self.analysis_scope.start_time,
#                 end_time=self.analysis_scope.end_time
#             )
#         )

#         print(
#             "[Analysis] Historical baselines ready."
#         )

#         print(
#             f"[Analysis] Baseline nodes: "
#             f"{len(baselines)}"
#         )

#         print(
#             "[Analysis] Running anomaly detection..."
#         )

#         result = self.analysis_system.analyze_time(
#             variable=variable,
#             time=time,
#             baselines_by_node=baselines
#         )

#         anomaly_field = result["anomaly_field"]
#         regions = result["regions"]

#         print(
#             "[Analysis] Anomaly field created."
#         )

#         print(
#             f"[Analysis] Anomalous nodes: "
#             f"{len(anomaly_field.get_anomalous_node_ids())}"
#         )

#         print(
#             f"[Analysis] Spatial regions: "
#             f"{len(regions)}"
#         )

#         print()
#         print(
#             "[Analysis] Single-timestamp analysis complete."
#         )
#         print()


#         weather_graph_builder = WeatherDataGraphBuilder(
#             weather_dataset=self.weather_dataset,
#             data_index=self.weather_data_index
#         )

#         self.weather_data_graph = (
#             weather_graph_builder.build(
#                 times=[time]
#             )
#         )
        
#         visualization_data = (
#             self.build_visualization_data(
#                 result
#             )
#         )

#         result["visualization"] = (
#             visualization_data
#         )

#         return result


#     def build_visualization_data(self, result):
#         """
#         Convert a single analysis result into
#         visualization-ready data.

#         The analysis system remains responsible for
#         producing domain objects.

#         The visualization serializer converts those
#         domain objects into a frontend-safe data contract.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.weather_data_index is None:
#             raise RuntimeError(
#                 "Weather data index has not been configured."
#             )

#         if result is None:
#             raise ValueError(
#                 "Analysis result cannot be None."
#             )

#         anomaly_field = result.get(
#             "anomaly_field"
#         )

#         regions = result.get(
#             "regions",
#             []
#         )

#         visualization_data = (
#             self.visualization_serializer.serialize(
#                 anomaly_field=anomaly_field,
#                 regions=regions,
#                 data_index=self.weather_data_index,
#                 weather_graph=self.weather_data_graph,
#                 variable=self.analysis_scope.variable
#             )
#         )

#         print(
#             "[Visualization] Visualization data created."
#         )

#         print(
#             f"[Visualization] Anomalies: "
#             f"{len(visualization_data.anomalies)}"
#         )

#         print(
#             f"[Visualization] Regions: "
#             f"{len(visualization_data.regions)}"
#         )

#         return visualization_data    

#     def build_visualization_timeline(self, result):
#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.weather_data_index is None:
#             raise RuntimeError(
#                 "Weather data index has not been configured."
#             )

#         if result is None:
#             raise ValueError(
#                 "Analysis result cannot be None."
#             )

#         timeline = self.visualization_serializer.serialize_timeline(
#             anomaly_fields=result["fields"],
#             region_fields=result["region_fields"],
#             tracks=result["tracks"],
#             events=result["events"],
#             data_index=self.weather_data_index,
#             weather_graph=self.weather_data_graph,
#             variable=result["variable"]
#         )

#         print(
#             "[Visualization] Visualization timeline created."
#         )

#         print(
#             f"[Visualization] Frames: "
#             f"{timeline.frame_count}"
#         )

#         print(
#             f"[Visualization] Tracks: "
#             f"{len(timeline.tracks)}"
#         )

#         print(
#             f"[Visualization] Events: "
#             f"{len(timeline.events)}"
#         )

#         return timeline

#     def run_analysis_range(self, times):
#         """
#         Run the complete spatio-temporal anomaly pipeline
#         over multiple timestamps.

#         Pipeline:

#             Historical Baseline
#                   ↓
#             Anomaly Detection
#                   ↓
#             Classification
#                   ↓
#             Anomaly Field
#                   ↓
#             Spatial Regions
#                   ↓
#             Temporal Tracking
#                   ↓
#             Weather Events

#         This is request-driven and is intentionally not
#         executed automatically every runtime tick.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized."
#             )

#         if self.analysis_system is None:
#             raise RuntimeError(
#                 "Analysis system has not been configured."
#             )

#         if self.analysis_scope is None:
#             raise RuntimeError(
#                 "Analysis scope has not been configured."
#             )

#         times = list(times)

#         if not times:
#             raise ValueError(
#                 "Analysis time range cannot be empty."
#             )

#         variable = self.analysis_scope.variable

#         print("========================================")
#         print("      AVANI TEMPORAL ANALYSIS")
#         print("========================================")
#         print()

#         print(
#             f"[Analysis] Variable: {variable}"
#         )

#         print(
#             f"[Analysis] Time steps: {len(times)}"
#         )

#         print(
#             f"[Analysis] Start: {times[0]}"
#         )

#         print(
#             f"[Analysis] End: {times[-1]}"
#         )

#         print()

#         print(
#             "[Analysis] Building historical baselines..."
#         )

#         baselines = (
#             self.analysis_system.build_baselines(
#                 variable=variable,
#                 start_time=self.analysis_scope.start_time,
#                 end_time=self.analysis_scope.end_time
#             )
#         )

#         print(
#             "[Analysis] Historical baselines ready."
#         )

#         print(
#             f"[Analysis] Baseline nodes: "
#             f"{len(baselines)}"
#         )

#         print()

#         print(
#             "[Analysis] Running spatio-temporal "
#             "anomaly analysis..."
#         )

#         result = (
#             self.analysis_system.analyze_time_range(
#                 variable=variable,
#                 times=times,
#                 baselines_by_node=baselines
#             )
#         )

#         print()

#         print(
#             "[Visualization] Building weather data graph..."
#         )

#         weather_graph_builder = WeatherDataGraphBuilder(
#             weather_dataset=self.weather_dataset,
#             data_index=self.weather_data_index
#         )

#         self.weather_data_graph = (
#             weather_graph_builder.build(
#                 times=times
#             )
#         )

#         print(
#             "[Visualization] Weather data graph created."
#         )

#         print(
#             f"[Visualization] Graph nodes: "
#             f"{self.weather_data_graph.get_node_count()}"
#         )

#         print(
#             f"[Visualization] Graph states: "
#             f"{self.weather_data_graph.get_state_count()}"
#         )

#         print(
#             f"[Visualization] Temporal edges: "
#             f"{self.weather_data_graph.get_temporal_edge_count()}"
#         )

#         visualization_timeline = (
#             self.build_visualization_timeline(result)
#         )

#         result["visualization_timeline"] = (
#             visualization_timeline
#         )


#         print()

#         print(
#             "[Analysis] Temporal analysis complete."
#         )

#         print(
#             f"[Analysis] Anomaly fields: "
#             f"{len(result['fields'])}"
#         )

#         print(
#             f"[Analysis] Region fields: "
#             f"{len(result['region_fields'])}"
#         )

#         print(
#             f"[Analysis] Tracks: "
#             f"{len(result['tracks'])}"
#         )

#         print(
#             f"[Analysis] Events: "
#             f"{len(result['events'])}"
#         )

#         print()

#         for track in result["tracks"]:
#             print(
#                 f"[Analysis] Track {track.track_id}: "
#                 f"category={track.category}, "
#                 f"regions={track.region_count}, "
#                 f"start={track.start_time}, "
#                 f"end={track.end_time}"
#             )

#         for event in result["events"]:
#             print(
#                 f"[Analysis] Event {event.event_id}: "
#                 f"category={event.category}, "
#                 f"duration={event.duration_steps}, "
#                 f"start={event.start_time}, "
#                 f"end={event.end_time}, "
#                 f"threat={event.threat_level}"
#             )

#         print()

#         return result

#     def update(self, delta_time):
#         """
#         Update the Avani application.

#         Expensive historical analysis is intentionally not
#         performed here every tick.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized "
#                 "before update()."
#             )

#         self.elapsed_time += delta_time
#         self.frame_count += 1

#         self._process_commands()
#         self._update_weather()
#         self._update_analysis()
#         self._publish_state()

#     def _process_commands(self):
#         """
#         Process application commands.

#         Later this will receive commands from the
#         JavaScript frontend.
#         """
#         pass

#     def _update_weather(self):
#         """
#         Service the weather subsystem.

#         Historical ERA5 data is currently accessed
#         on demand.
#         """
#         pass

#     def _update_analysis(self):
#         """
#         Service analysis systems.

#         Heavy analysis remains request-driven.
#         """
#         pass

#     def _publish_state(self):
#         """
#         Publish application state to consumers.

#         Later this becomes part of the Python ↔ JS
#         communication layer.
#         """
#         pass

#     def should_close(self):
#         return self._should_close

#     def request_close(self):
#         """
#         Request application shutdown.
#         """

#         self._should_close = True

#     def shutdown(self):
#         """
#         Shut down all application systems in reverse
#         ownership order.
#         """

#         if not self._initialized:
#             return

#         print()
#         print("[Avani] Shutting down...")

#         if self.analysis_system is not None:
#             self.analysis_system.shutdown()
#             self.analysis_system = None

#         self.weather_data_index = None
#         self.weather_data_graph = None
#         self.analysis_scope = None
#         self.weather_frame_service = None

#         if self.weather_dataset is not None:
#             self.weather_dataset.close()
#             self.weather_dataset = None

#         self.weather_bridge = None

#         self._initialized = False

#         print(
#             "[Avani] Application shutdown complete."
#         )

#     def run(self, application_loop):
#         """
#         Run the application using the supplied
#         application loop.
#         """

#         if not self._initialized:
#             raise RuntimeError(
#                 "AvaniApplication must be initialized "
#                 "before run()."
#             )

#         application_loop.run()



from application.analysis_scope import AnalysisScope
from application.analysis_system import AnalysisSystem

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset
from weather.weather_data_index import WeatherDataIndex
from weather.weather_data_graph_builder import (
    WeatherDataGraphBuilder
)

from visualization.visualization_serializer import (
    VisualizationSerializer
)

from application.weather_frame_service import WeatherFrameService


class AvaniApplication:
    """
    Main application object for Avani.

    AvaniApplication owns the lifetime of the major backend systems.

    Individual weather, anomaly, tracking, event, and AI classes
    remain responsible for their own domain logic.

    This class is responsible for orchestration and application
    lifecycle.
    """

    def __init__(self, weather_data_root):
        self.weather_data_root = weather_data_root

        self.weather_bridge = None
        self.weather_dataset = None
        self.weather_frame_service = None

        self.weather_data_index = None
        self.weather_data_graph = None
        self.analysis_system = None

        self.visualization_serializer = (
            VisualizationSerializer()
        )

        self.analysis_scope = None

        self._initialized = False
        self._should_close = False

        self.elapsed_time = 0.0
        self.frame_count = 0

    def initialize(self):
        """Initialize the Avani backend."""

        if self._initialized:
            raise RuntimeError(
                "AvaniApplication is already initialized."
            )

        print("========================================")
        print("           AVANI APPLICATION")
        print("========================================")
        print()
        print("[Avani] Initializing application...")
        print()

        self._initialize_weather_system()

        self.weather_frame_service = WeatherFrameService(
            self.weather_dataset
        )

        self._initialized = True

        print()
        print("[Avani] Application initialized.")
        print("[Avani] Runtime ready.")
        print()

    def _initialize_weather_system(self):
        print("[Weather] Initializing weather data system...")

        self.weather_bridge = WeatherDataBridge(
            self.weather_data_root
        )

        self.weather_dataset = WeatherDataset(
            self.weather_bridge
        )

        print(
            f"[Weather] Data root: "
            f"{self.weather_data_root}"
        )

        print("[Weather] Opening ERA5 dataset...")

        self.weather_dataset.open()

        print("[Weather] ERA5 dataset opened.")
        print("[Weather] Weather data system ready.")

    def get_temperature_frame(
        self,
        time,
        min_latitude=-90.0,
        max_latitude=90.0,
        min_longitude=-180.0,
        max_longitude=180.0,
        max_rows=91,
        max_columns=180,
    ):
        """Return a visualization-ready temperature frame."""

        self._ensure_initialized()

        if self.weather_frame_service is None:
            raise RuntimeError(
                "WeatherFrameService is not initialized."
            )

        return self.weather_frame_service.get_temperature_frame(
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            max_rows=max_rows,
            max_columns=max_columns,
        )

    def get_weather_frame(
        self,
        variable,
        time,
        min_latitude=-90.0,
        max_latitude=90.0,
        min_longitude=-180.0,
        max_longitude=180.0,
        max_rows=91,
        max_columns=180,
    ):
        """Request a sampled weather field."""

        self._ensure_initialized()

        if self.weather_frame_service is None:
            raise RuntimeError(
                "WeatherFrameService is not initialized."
            )

        return self.weather_frame_service.get_weather_frame(
            variable=variable,
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            max_rows=max_rows,
            max_columns=max_columns,
        )

    def get_weather_time_series(
        self,
        variable,
        start_time,
        end_time,
        latitude,
        longitude,
        time_step=1,
    ):
        """
        Request a converted weather time series.

        The persistent WeatherDataset handles data access
        and unit conversion. This method exposes that capability
        through the application API.
        """

        self._ensure_initialized()

        if self.weather_dataset is None:
            raise RuntimeError(
                "WeatherDataset is not initialized."
            )

        return self.weather_dataset.get_time_series(
            variable=variable,
            start_time=start_time,
            end_time=end_time,
            latitude=latitude,
            longitude=longitude,
            time_step=time_step,
        )

    def configure_analysis(self, scope):
        """Configure the geographic analysis world."""

        self._ensure_initialized()

        if not isinstance(scope, AnalysisScope):
            raise TypeError(
                "scope must be an AnalysisScope."
            )

        if self.analysis_system is not None:
            raise RuntimeError(
                "Analysis has already been configured."
            )

        self.analysis_scope = scope

        print("[Analysis] Configuring analysis scope...")
        print(f"[Analysis] Variable: {scope.variable}")

        print(
            "[Analysis] Latitude: "
            f"{scope.min_latitude} → {scope.max_latitude}"
        )

        print(
            "[Analysis] Longitude: "
            f"{scope.min_longitude} → {scope.max_longitude}"
        )

        self.weather_data_index = WeatherDataIndex(
            self.weather_dataset.grid_index
        )

        self.weather_data_index.build(
            min_latitude=scope.min_latitude,
            max_latitude=scope.max_latitude,
            min_longitude=scope.min_longitude,
            max_longitude=scope.max_longitude,
        )

        print("[Analysis] Spatial index created.")

        print(
            f"[Analysis] Spatial nodes: "
            f"{self.weather_data_index.get_node_count()}"
        )

        self.analysis_system = AnalysisSystem(
            weather_bridge=self.weather_bridge,
            weather_dataset=self.weather_dataset,
            data_index=self.weather_data_index,
        )

        self.analysis_system.initialize()

        print("[Analysis] Analysis system configured.")
        print()

    def run_analysis(self, time):
        """Run a complete analysis for one timestamp."""

        self._ensure_initialized()

        if self.analysis_system is None:
            raise RuntimeError(
                "Analysis system has not been configured."
            )

        variable = self.analysis_scope.variable

        print("========================================")
        print("          AVANI ANALYSIS")
        print("========================================")
        print()
        print(f"[Analysis] Variable: {variable}")
        print(f"[Analysis] Time: {time}")
        print("[Analysis] Building historical baselines...")

        baselines = self.analysis_system.build_baselines(
            variable=variable,
            start_time=self.analysis_scope.start_time,
            end_time=self.analysis_scope.end_time,
        )

        print("[Analysis] Historical baselines ready.")
        print(f"[Analysis] Baseline nodes: {len(baselines)}")
        print("[Analysis] Running anomaly detection...")

        result = self.analysis_system.analyze_time(
            variable=variable,
            time=time,
            baselines_by_node=baselines,
        )

        anomaly_field = result["anomaly_field"]
        regions = result["regions"]

        print("[Analysis] Anomaly field created.")

        print(
            f"[Analysis] Anomalous nodes: "
            f"{len(anomaly_field.get_anomalous_node_ids())}"
        )

        print(f"[Analysis] Spatial regions: {len(regions)}")
        print()
        print("[Analysis] Single-timestamp analysis complete.")
        print()

        weather_graph_builder = WeatherDataGraphBuilder(
            weather_dataset=self.weather_dataset,
            data_index=self.weather_data_index,
        )

        self.weather_data_graph = weather_graph_builder.build(
            times=[time]
        )

        visualization_data = self.build_visualization_data(
            result
        )

        result["visualization"] = visualization_data

        return result

    def build_visualization_data(self, result):
        """Serialize a single analysis result for visualization."""

        self._ensure_initialized()

        if self.weather_data_index is None:
            raise RuntimeError(
                "Weather data index has not been configured."
            )

        if result is None:
            raise ValueError(
                "Analysis result cannot be None."
            )

        visualization_data = self.visualization_serializer.serialize(
            anomaly_field=result.get("anomaly_field"),
            regions=result.get("regions", []),
            data_index=self.weather_data_index,
            weather_graph=self.weather_data_graph,
            variable=self.analysis_scope.variable,
        )

        print("[Visualization] Visualization data created.")
        print(
            f"[Visualization] Anomalies: "
            f"{len(visualization_data.anomalies)}"
        )
        print(
            f"[Visualization] Regions: "
            f"{len(visualization_data.regions)}"
        )

        return visualization_data

    def build_visualization_timeline(self, result):
        """Serialize a temporal analysis timeline."""

        self._ensure_initialized()

        if self.weather_data_index is None:
            raise RuntimeError(
                "Weather data index has not been configured."
            )

        if result is None:
            raise ValueError(
                "Analysis result cannot be None."
            )

        timeline = self.visualization_serializer.serialize_timeline(
            anomaly_fields=result["fields"],
            region_fields=result["region_fields"],
            tracks=result["tracks"],
            events=result["events"],
            data_index=self.weather_data_index,
            weather_graph=self.weather_data_graph,
            variable=result["variable"],
        )

        print("[Visualization] Visualization timeline created.")
        print(f"[Visualization] Frames: {timeline.frame_count}")
        print(f"[Visualization] Tracks: {len(timeline.tracks)}")
        print(f"[Visualization] Events: {len(timeline.events)}")

        return timeline

    def run_analysis_range(self, times):
        """Run spatio-temporal anomaly analysis over multiple times."""

        self._ensure_initialized()

        if self.analysis_system is None:
            raise RuntimeError(
                "Analysis system has not been configured."
            )

        if self.analysis_scope is None:
            raise RuntimeError(
                "Analysis scope has not been configured."
            )

        times = list(times)

        if not times:
            raise ValueError(
                "Analysis time range cannot be empty."
            )

        variable = self.analysis_scope.variable

        print("========================================")
        print("      AVANI TEMPORAL ANALYSIS")
        print("========================================")
        print()
        print(f"[Analysis] Variable: {variable}")
        print(f"[Analysis] Time steps: {len(times)}")
        print(f"[Analysis] Start: {times[0]}")
        print(f"[Analysis] End: {times[-1]}")
        print()
        print("[Analysis] Building historical baselines...")

        baselines = self.analysis_system.build_baselines(
            variable=variable,
            start_time=self.analysis_scope.start_time,
            end_time=self.analysis_scope.end_time,
        )

        print("[Analysis] Historical baselines ready.")
        print(f"[Analysis] Baseline nodes: {len(baselines)}")
        print()
        print(
            "[Analysis] Running spatio-temporal anomaly analysis..."
        )

        result = self.analysis_system.analyze_time_range(
            variable=variable,
            times=times,
            baselines_by_node=baselines,
        )

        print()
        print("[Visualization] Building weather data graph...")

        weather_graph_builder = WeatherDataGraphBuilder(
            weather_dataset=self.weather_dataset,
            data_index=self.weather_data_index,
        )

        self.weather_data_graph = weather_graph_builder.build(
            times=times
        )

        print("[Visualization] Weather data graph created.")
        print(
            f"[Visualization] Graph nodes: "
            f"{self.weather_data_graph.get_node_count()}"
        )
        print(
            f"[Visualization] Graph states: "
            f"{self.weather_data_graph.get_state_count()}"
        )
        print(
            f"[Visualization] Temporal edges: "
            f"{self.weather_data_graph.get_temporal_edge_count()}"
        )

        visualization_timeline = (
            self.build_visualization_timeline(result)
        )

        result["visualization_timeline"] = visualization_timeline

        print()
        print("[Analysis] Temporal analysis complete.")
        print(f"[Analysis] Anomaly fields: {len(result['fields'])}")
        print(
            f"[Analysis] Region fields: "
            f"{len(result['region_fields'])}"
        )
        print(f"[Analysis] Tracks: {len(result['tracks'])}")
        print(f"[Analysis] Events: {len(result['events'])}")
        print()

        for track in result["tracks"]:
            print(
                f"[Analysis] Track {track.track_id}: "
                f"category={track.category}, "
                f"regions={track.region_count}, "
                f"start={track.start_time}, "
                f"end={track.end_time}"
            )

        for event in result["events"]:
            print(
                f"[Analysis] Event {event.event_id}: "
                f"category={event.category}, "
                f"duration={event.duration_steps}, "
                f"start={event.start_time}, "
                f"end={event.end_time}, "
                f"threat={event.threat_level}"
            )

        print()

        return result

    def update(self, delta_time):
        """Update lightweight application runtime systems."""

        self._ensure_initialized()

        self.elapsed_time += delta_time
        self.frame_count += 1

        self._process_commands()
        self._update_weather()
        self._update_analysis()
        self._publish_state()

    def _process_commands(self):
        """Process commands from application consumers."""
        pass

    def _update_weather(self):
        """Service weather systems; ERA5 requests are on demand."""
        pass

    def _update_analysis(self):
        """Service analysis systems without running heavy analysis each tick."""
        pass

    def _publish_state(self):
        """Publish application state to consumers."""
        pass

    def should_close(self):
        return self._should_close

    def request_close(self):
        """Request application shutdown."""
        self._should_close = True

    def shutdown(self):
        """Shut down application systems in reverse ownership order."""

        if not self._initialized:
            return

        print()
        print("[Avani] Shutting down...")

        if self.analysis_system is not None:
            self.analysis_system.shutdown()
            self.analysis_system = None

        self.weather_data_index = None
        self.weather_data_graph = None
        self.analysis_scope = None
        self.weather_frame_service = None

        if self.weather_dataset is not None:
            self.weather_dataset.close()
            self.weather_dataset = None

        self.weather_bridge = None
        self._initialized = False

        print("[Avani] Application shutdown complete.")

    def run(self, application_loop):
        """Run the application using the supplied application loop."""

        self._ensure_initialized()
        application_loop.run()

    def _ensure_initialized(self):
        """Guard public operations that require an active runtime."""

        if not self._initialized:
            raise RuntimeError(
                "AvaniApplication must be initialized."
            )
    
    def reset_analysis(self):
        """Release the current analysis configuration, if any."""

        if self.analysis_system is not None:
            self.analysis_system.shutdown()
            self.analysis_system = None

        self.weather_data_index = None
        self.weather_data_graph = None
        self.analysis_scope = None
