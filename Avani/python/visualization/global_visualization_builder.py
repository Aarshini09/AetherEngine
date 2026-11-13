
import json
from pathlib import Path

import numpy as np

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


class GlobalVisualizationBuilder:
    """
    Exports a time range into a static global visualization JSON.

    Data access and unit conversion are delegated to WeatherDataset.
    """

    def __init__(
        self,
        source_path,
        output_path,
        variable="temperature",
        spatial_step=8,
        weather_dataset=None,
    ):
        self.source_path = (
            Path(source_path) if source_path is not None else None
        )
        self.output_path = Path(output_path)
        self.variable = variable
        self.spatial_step = spatial_step

        self.weather_dataset = weather_dataset
        self._owns_dataset = weather_dataset is None

    def build(self, start_time, end_time):
        if self.spatial_step <= 0:
            raise ValueError(
                "spatial_step must be greater than zero."
            )

        if self._owns_dataset:
            if self.source_path is None:
                raise ValueError(
                    "source_path is required when no WeatherDataset "
                    "is provided."
                )

            if not self.source_path.exists():
                raise FileNotFoundError(
                    f"ERA5 source file not found: {self.source_path}"
                )

            # The bridge expects its directory to contain the
            # configured ERA5 source files.
            bridge = WeatherDataBridge(self.source_path.parent)
            self.weather_dataset = WeatherDataset(bridge)

            try:
                self.weather_dataset.open()
                return self._build_open_dataset(start_time, end_time)
            finally:
                self.weather_dataset.close()
                self.weather_dataset = None

        if self.weather_dataset is None:
            raise RuntimeError("WeatherDataset is unavailable.")

        return self._build_open_dataset(start_time, end_time)

    def _build_open_dataset(self, start_time, end_time):
        print()
        print("[GlobalVisualization] Building global timeline")
        print(f"  Variable: {self.variable}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")

        # Use the existing bridge to resolve the source reader.
        reader = self.weather_dataset.bridge.get_reader(
            self.variable
        )
        available_times = reader.get_times().values

        start = np.datetime64(start_time)
        end = np.datetime64(end_time)

        if start > end:
            raise ValueError(
                "start_time must not be later than end_time."
            )

        selected_times = available_times[
            (available_times >= start) &
            (available_times <= end)
        ]

        frames = []

        for index, timestamp in enumerate(selected_times):
            weather_field = self.weather_dataset.get_field(
                variable=self.variable,
                time=timestamp,
                min_latitude=-90.0,
                max_latitude=90.0,
                # ERA5 commonly stores longitudes in [0, 360).
                min_longitude=-180.0,
                max_longitude=180.0,
            )

            field = weather_field.data

            # Sample while the field can still be lazy.
            sampled = field.isel(
                latitude=slice(None, None, self.spatial_step),
                longitude=slice(None, None, self.spatial_step),
            )

            latitudes = np.asarray(sampled.latitude.values)
            longitudes = np.asarray(sampled.longitude.values)
            values_array = np.asarray(sampled.values)

            values = []
            node_id = 0

            for row, latitude in enumerate(latitudes):
                for column, longitude in enumerate(longitudes):
                    value = float(values_array[row, column])

                    if not np.isfinite(value):
                        continue

                    values.append({
                        "node_id": node_id,
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "value": value,
                    })
                    node_id += 1

            timestamp_text = str(weather_field.time)

            frames.append({
                "time": timestamp_text,
                "variable": weather_field.variable,
                "values": values,
                "anomalies": [],
                "regions": [],
                "tracks": [],
                "events": [],
            })

            print(
                "[GlobalVisualization] "
                f"Frame {index + 1}/{len(selected_times)}: "
                f"{timestamp_text} ({len(values)} values)"
            )

        output = {
            "variable": self.variable,
            "start_time": frames[0]["time"] if frames else None,
            "end_time": frames[-1]["time"] if frames else None,
            "frame_count": len(frames),
            "spatial_step": self.spatial_step,
            "global": True,
            "frames": frames,
        }

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output_path.write_text(
            json.dumps(output, allow_nan=False),
            encoding="utf-8",
        )

        print()
        print("[GlobalVisualization] Global visualization written:")
        print(f"  {self.output_path}")

        return output
