from visualization.visualization_data import VisualizationData
from visualization.visualization_timeline import VisualizationTimeline


class VisualizationSerializer:
    """
    Converts weather-analysis domain objects into
    visualization-ready data.

    This class forms the boundary between the analysis
    system and the visualization system.

    It does not perform analysis.
    """

    def serialize(
        self,
        anomaly_field=None,
        regions=None,
        tracks=None,
        events=None,
        data_index=None,
        weather_graph=None,
        variable=None
    ):
        regions = (
            [] if regions is None
            else list(regions)
        )

        tracks = (
            [] if tracks is None
            else list(tracks)
        )

        events = (
            [] if events is None
            else list(events)
        )

        if anomaly_field is not None:

            anomalies = self._serialize_anomalies(
                anomaly_field=anomaly_field,
                data_index=data_index
            )

            if variable is None:
                variable = self._infer_variable(
                    anomaly_field
                )

            time = anomaly_field.time

        else:
            anomalies = []
            time = None

        values = self._serialize_values(
            time=time,
            variable=variable,
            weather_graph=weather_graph
        )

        serialized_regions = self._serialize_regions(
            regions=regions,
            data_index=data_index
        )

        serialized_tracks = self._serialize_tracks(
            tracks=tracks
        )

        serialized_events = self._serialize_events(
            events=events
        )

        return VisualizationData(
            time=time,
            variable=variable,
            values=values,
            anomalies=anomalies,
            regions=serialized_regions,
            tracks=serialized_tracks,
            events=serialized_events
        )

    def serialize_timeline(
        self,
        anomaly_fields,
        region_fields,
        tracks=None,
        events=None,
        data_index=None,
        weather_graph=None,
        variable=None
    ):
        anomaly_fields = (
            [] if anomaly_fields is None
            else list(anomaly_fields)
        )

        region_fields = (
            [] if region_fields is None
            else list(region_fields)
        )

        tracks = (
            [] if tracks is None
            else list(tracks)
        )

        events = (
            [] if events is None
            else list(events)
        )

        timeline = VisualizationTimeline(
            variable=variable
        )

        for anomaly_field, region_field in zip(
            anomaly_fields,
            region_fields
        ):
            frame = self.serialize(
                anomaly_field=anomaly_field,
                regions=region_field["regions"],
                data_index=data_index,
                weather_graph=weather_graph,
                variable=variable
            )

            timeline.add_frame(frame)

        timeline.tracks = self._serialize_tracks(
            tracks
        )

        timeline.events = self._serialize_events(
            events
        )

        return timeline

    def _serialize_values(
        self,
        time,
        variable,
        weather_graph
    ):
        """
        Serialize the actual weather value at every
        spatial node for one timestamp.

        WeatherState remains the source of truth.
        """

        if weather_graph is None:
            return []

        if time is None:
            return []

        if variable is None:
            return []

        values = []

        for node_id in weather_graph.node_series:

            try:
                state = weather_graph.get_state(
                    node_id=node_id,
                    time=time
                )

            except KeyError:
                continue

            node = weather_graph.get_node(
                node_id
            )

            value = self._extract_variable_value(
                state=state,
                variable=variable
            )

            if value is None:
                continue

            values.append({
                "node_id": int(node_id),
                "latitude": float(
                    node.coordinate.latitude
                ),
                "longitude": float(
                    node.coordinate.longitude
                ),
                "value": float(value)
            })

        return values

    def _extract_variable_value(
        self,
        state,
        variable
    ):
        """
        Extract a visualization variable from
        WeatherState.

        The mapping is explicit so the visualization
        layer has a stable definition of every supported
        weather variable.
        """

        if state is None:
            return None

        if variable == "temperature":
            return state.temperature

        if variable == "dewpoint":
            return state.dewpoint

        if variable == "mean_sea_level_pressure":
            return state.mean_sea_level_pressure

        if variable == "surface_pressure":
            return state.surface_pressure

        if variable == "wind_u":
            return state.wind_u

        if variable == "wind_v":
            return state.wind_v

        if variable == "wind_speed":
            return state.wind_speed

        if variable == "total_precipitation":
            return state.total_precipitation

        return None

    def _serialize_anomalies(
        self,
        anomaly_field,
        data_index
    ):
        anomalies = []

        for node_id, anomaly in (
            anomaly_field.anomalies.items()
        ):
            classification = (
                anomaly_field.classifications.get(
                    node_id
                )
            )

            latitude = anomaly.latitude
            longitude = anomaly.longitude

            if data_index is not None:

                try:
                    node = data_index.get_node(
                        node_id
                    )

                    latitude = (
                        node.coordinate.latitude
                    )

                    longitude = (
                        node.coordinate.longitude
                    )

                except KeyError:
                    pass

            anomaly_data = {
                "node_id": int(node_id),

                "variable": anomaly.variable,

                "time": self._serialize_time(
                    anomaly.time
                ),

                "latitude": float(latitude),

                "longitude": float(longitude),

                "value": float(
                    anomaly.value
                ),

                "baseline_mean": float(
                    anomaly.baseline_mean
                ),

                "baseline_standard_deviation": float(
                    anomaly.baseline_standard_deviation
                ),

                "absolute_anomaly": float(
                    anomaly.absolute_anomaly
                ),

                "standardized_anomaly": (
                    None
                    if anomaly.standardized_anomaly is None
                    else float(
                        anomaly.standardized_anomaly
                    )
                ),

                "is_anomaly": bool(
                    anomaly.is_anomaly
                ),

                "severity": anomaly.severity
            }

            if classification is not None:

                anomaly_data.update({
                    "category": classification.category,

                    "direction": classification.direction,

                    "is_extreme": bool(
                        classification.is_extreme
                    )
                })

            else:

                anomaly_data.update({
                    "category": None,

                    "direction": None,

                    "is_extreme": False
                })

            anomalies.append(
                anomaly_data
            )

        return anomalies

    def _serialize_regions(
        self,
        regions,
        data_index
    ):
        serialized_regions = []

        for region in regions:

            node_locations = []

            for node_id in region.node_ids:

                if data_index is None:
                    continue

                try:
                    node = data_index.get_node(
                        node_id
                    )

                except KeyError:
                    continue

                node_locations.append({
                    "node_id": int(node_id),

                    "latitude": float(
                        node.coordinate.latitude
                    ),

                    "longitude": float(
                        node.coordinate.longitude
                    )
                })

            serialized_regions.append({
                "region_id": int(
                    region.region_id
                ),

                "time": self._serialize_time(
                    region.time
                ),

                "category": region.category,

                "node_ids": [
                    int(node_id)
                    for node_id in region.node_ids
                ],

                "nodes": node_locations,

                "min_latitude": (
                    None
                    if region.min_latitude is None
                    else float(
                        region.min_latitude
                    )
                ),

                "max_latitude": (
                    None
                    if region.max_latitude is None
                    else float(
                        region.max_latitude
                    )
                ),

                "min_longitude": (
                    None
                    if region.min_longitude is None
                    else float(
                        region.min_longitude
                    )
                ),

                "max_longitude": (
                    None
                    if region.max_longitude is None
                    else float(
                        region.max_longitude
                    )
                ),

                "node_count": int(
                    region.node_count
                ),

                "latitude_span": float(
                    region.latitude_span
                ),

                "longitude_span": float(
                    region.longitude_span
                ),

                "min_value": self._optional_float(
                    region.min_value
                ),

                "max_value": self._optional_float(
                    region.max_value
                ),

                "mean_value": self._optional_float(
                    region.mean_value
                ),

                "min_standardized_anomaly": (
                    self._optional_float(
                        region.min_standardized_anomaly
                    )
                ),

                "max_standardized_anomaly": (
                    self._optional_float(
                        region.max_standardized_anomaly
                    )
                ),

                "mean_standardized_anomaly": (
                    self._optional_float(
                        region.mean_standardized_anomaly
                    )
                )
            })

        return serialized_regions

    def _serialize_tracks(
        self,
        tracks
    ):
        serialized_tracks = []

        for track in tracks:

            serialized_regions = []

            for region in track.regions:

                center_latitude = self._center(
                    region.min_latitude,
                    region.max_latitude
                )

                center_longitude = self._center(
                    region.min_longitude,
                    region.max_longitude
                )

                serialized_regions.append({
                    "region_id": int(
                        region.region_id
                    ),

                    "time": self._serialize_time(
                        region.time
                    ),

                    "category": region.category,

                    "center": {
                        "latitude": center_latitude,
                        "longitude": center_longitude
                    },

                    "min_latitude": (
                        self._optional_float(
                            region.min_latitude
                        )
                    ),

                    "max_latitude": (
                        self._optional_float(
                            region.max_latitude
                        )
                    ),

                    "min_longitude": (
                        self._optional_float(
                            region.min_longitude
                        )
                    ),

                    "max_longitude": (
                        self._optional_float(
                            region.max_longitude
                        )
                    ),

                    "node_count": int(
                        region.node_count
                    )
                })

            serialized_lifecycle_events = []

            for event in getattr(
                track,
                "lifecycle_events",
                []
            ):
                if isinstance(event, dict):

                    serialized_event = {}

                    for key, value in event.items():

                        if key == "time":
                            serialized_event[key] = (
                                self._serialize_time(value)
                            )

                        elif key.endswith("_track_id"):
                            serialized_event[key] = (
                                None
                                if value is None
                                else int(value)
                            )

                        elif key.endswith("_track_ids"):
                            serialized_event[key] = (
                                None
                                if value is None
                                else [
                                    int(track_id)
                                    for track_id in value
                                ]
                            )

                        else:
                            serialized_event[key] = value

                    serialized_lifecycle_events.append(
                        serialized_event
                    )

                else:
                    serialized_lifecycle_events.append(
                        event
                    )

            serialized_tracks.append({
                "track_id": int(
                    track.track_id
                ),

                "category": track.category,

                "start_time": self._serialize_time(
                    track.start_time
                ),

                "end_time": self._serialize_time(
                    track.end_time
                ),

                "region_count": int(
                    track.region_count
                ),

                "duration_steps": int(
                    track.duration_count
                ),

                "regions": serialized_regions,

                "parent_track_ids": sorted(
                    int(track_id)
                    for track_id in getattr(
                        track,
                        "parent_track_ids",
                        set()
                    )
                ),

                "child_track_ids": sorted(
                    int(track_id)
                    for track_id in getattr(
                        track,
                        "child_track_ids",
                        set()
                    )
                ),

                "merged_into_track_ids": sorted(
                    int(track_id)
                    for track_id in getattr(
                        track,
                        "merged_into_track_ids",
                        set()
                    )
                ),

                "merged_from_track_ids": sorted(
                    int(track_id)
                    for track_id in getattr(
                        track,
                        "merged_from_track_ids",
                        set()
                    )
                ),

                "lifecycle_events": (
                    serialized_lifecycle_events
                )
            })

        return serialized_tracks
    def _serialize_events(
        self,
        events
    ):
        serialized_events = []

        for event in events:

            serialized_events.append({
                "event_id": int(
                    event.event_id
                ),

                "category": event.category,

                "start_time": self._serialize_time(
                    event.start_time
                ),

                "end_time": self._serialize_time(
                    event.end_time
                ),

                "region_count": int(
                    event.region_count
                ),

                "duration_steps": int(
                    event.duration_steps
                ),

                "start_location": self._location(
                    event.start_latitude,
                    event.start_longitude
                ),

                "end_location": self._location(
                    event.end_latitude,
                    event.end_longitude
                ),

                "has_movement": bool(
                    event.has_movement
                ),

                "minimum_value": (
                    self._optional_float(
                        event.minimum_value
                    )
                ),

                "maximum_value": (
                    self._optional_float(
                        event.maximum_value
                    )
                ),

                "minimum_standardized_anomaly": (
                    self._optional_float(
                        event.minimum_standardized_anomaly
                    )
                ),

                "maximum_standardized_anomaly": (
                    self._optional_float(
                        event.maximum_standardized_anomaly
                    )
                ),

                "threat_level": event.threat_level
            })

        return serialized_events

    def _infer_variable(
        self,
        anomaly_field
    ):
        for anomaly in (
            anomaly_field.anomalies.values()
        ):
            return anomaly.variable

        return None

    @staticmethod
    def _serialize_time(value):
        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        return str(value)

    @staticmethod
    def _optional_float(value):
        if value is None:
            return None

        return float(value)

    @staticmethod
    def _center(
        minimum,
        maximum
    ):
        if minimum is None or maximum is None:
            return None

        return (
            float(minimum) +
            float(maximum)
        ) / 2.0

    @staticmethod
    def _location(
        latitude,
        longitude
    ):
        if (
            latitude is None or
            longitude is None
        ):
            return None

        return {
            "latitude": float(latitude),
            "longitude": float(longitude)
        }

    def _serialize_track_relationships(self, track):
        return {
            "parent_track_ids": sorted(
                int(track_id)
                for track_id in track.parent_track_ids
            ),
            "child_track_ids": sorted(
                int(track_id)
                for track_id in track.child_track_ids
            ),
            "merged_into_track_ids": sorted(
                int(track_id)
                for track_id in track.merged_into_track_ids
            ),
            "merged_from_track_ids": sorted(
                int(track_id)
                for track_id in track.merged_from_track_ids
            ),
            "lifecycle_events": [
                {
                    "event_type": event["event_type"],
                    "time": self._serialize_time(event["time"]),
                    **{
                        key: value
                        for key, value in event.items()
                        if key not in ("event_type", "time")
                    }
                }
                for event in track.lifecycle_events
            ]
        }