
from math import isfinite
import numpy as np


class WeatherFrameService:
    """
    Builds compact, JSON-safe weather frames on demand.

    WeatherDataset owns data access and unit conversion.
    This service owns validation, spatial sampling,
    metadata, and serialization.
    """

    def __init__(self, weather_dataset):
        if weather_dataset is None:
            raise ValueError("weather_dataset cannot be None.")

        self.weather_dataset = weather_dataset

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
        self._validate_request(
            variable,
            time,
            min_latitude,
            max_latitude,
            min_longitude,
            max_longitude,
            max_rows,
            max_columns,
        )

        weather_field = self.weather_dataset.get_field(
            variable=variable,
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )

        field = weather_field.data

        if field.ndim != 2:
            raise ValueError(
                "Expected a 2D latitude-longitude field; "
                f"received shape {field.shape}."
            )

        if (
            "latitude" not in field.sizes
            or "longitude" not in field.sizes
        ):
            raise ValueError(
                "Weather field must contain latitude "
                "and longitude dimensions."
            )

        source_height = int(field.sizes["latitude"])
        source_width = int(field.sizes["longitude"])

        if source_height == 0 or source_width == 0:
            raise ValueError(
                "The requested geographic region contains no data."
            )

        # Choose evenly spaced source indices while preserving
        # both ends of each axis. Output dimensions never exceed
        # the requested maximums.
        row_indices = np.linspace(
            0,
            source_height - 1,
            num=min(max_rows, source_height),
            dtype=int,
        )

        column_indices = np.linspace(
            0,
            source_width - 1,
            num=min(max_columns, source_width),
            dtype=int,
        )

        # Select before reading values into memory.
        sampled_field = field.isel(
            latitude=row_indices,
            longitude=column_indices,
        )

        latitudes = np.asarray(
            sampled_field["latitude"].values
        )

        longitudes = np.asarray(
            sampled_field["longitude"].values
        )

        values = np.asarray(sampled_field.values)

        safe_values = []
        for value in values.ravel():
            numeric_value = float(value)
            safe_values.append(
                numeric_value if isfinite(numeric_value) else None
            )

        width = len(longitudes)
        height = len(latitudes)

        # Preserve the existing stride fields for compatibility.
        row_step = (
            int(np.diff(row_indices)[0])
            if len(row_indices) > 1
            else 1
        )
        column_step = (
            int(np.diff(column_indices)[0])
            if len(column_indices) > 1
            else 1
        )

        return {
            "variable": weather_field.variable,
            "unit": weather_field.unit,
            "time": str(weather_field.time),

            "grid": {
                "type": "regular_latitude_longitude",
                "latitude_dimension": "latitude",
                "longitude_dimension": "longitude",
                "latitude_order": (
                    "north_to_south"
                    if height < 2 or latitudes[0] >= latitudes[-1]
                    else "south_to_north"
                ),
                "longitude_convention": (
                    "0_to_360"
                    if len(longitudes) > 0
                    and np.min(longitudes) >= 0
                    and np.max(longitudes) > 180
                    else "minus180_to_180"
                ),
                "value_layout": "row_major",
                "missing_value": None,
            },

            "region": {
                "min_latitude": float(min_latitude),
                "max_latitude": float(max_latitude),
                "min_longitude": float(min_longitude),
                "max_longitude": float(max_longitude),
            },

            "width": int(width),
            "height": int(height),
            "latitudes": [float(v) for v in latitudes],
            "longitudes": [float(v) for v in longitudes],
            "values": safe_values,

            "source_width": source_width,
            "source_height": source_height,
            "row_step": row_step,
            "column_step": column_step,
            "sampling": "endpoint_preserving_uniform_indices",
        }

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
        """Backward-compatible temperature frame helper."""
        return self.get_weather_frame(
            variable="temperature",
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            max_rows=max_rows,
            max_columns=max_columns,
        )

    @staticmethod
    def _validate_request(
        variable,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
        max_rows,
        max_columns,
    ):
        if not isinstance(variable, str) or not variable.strip():
            raise ValueError("variable must be a non-empty string.")

        if time is None or not str(time).strip():
            raise ValueError("time must be provided.")

        if min_latitude > max_latitude:
            raise ValueError(
                "min_latitude must not exceed max_latitude."
            )

        if min_longitude > max_longitude:
            raise ValueError(
                "min_longitude must not exceed max_longitude. "
                "Antimeridian-crossing requests are not supported."
            )

        if not -90 <= min_latitude <= 90:
            raise ValueError("min_latitude must be between -90 and 90.")

        if not -90 <= max_latitude <= 90:
            raise ValueError("max_latitude must be between -90 and 90.")

        if not -180 <= min_longitude <= 180:
            raise ValueError(
                "min_longitude must be between -180 and 180."
            )

        if not -180 <= max_longitude <= 180:
            raise ValueError(
                "max_longitude must be between -180 and 180."
            )

        for name, value in (
            ("max_rows", max_rows),
            ("max_columns", max_columns),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, np.integer))
                or value < 1
            ):
                raise ValueError(
                    f"{name} must be a positive integer."
                )
