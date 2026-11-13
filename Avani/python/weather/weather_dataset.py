import numpy as np
from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_value import WeatherValue
from weather.weather_field import WeatherField
from weather.weather_state import WeatherState
from weather.weather_grid_index import WeatherGridIndex
from weather.weather_variables import WEATHER_VARIABLES
from weather.regional_weather_statistics import (
    RegionalWeatherStatistics,
)

class WeatherDataset:
    """
    High-level interface for application weather data.

    WeatherDataset coordinates:
        - weather data access
        - variable conversion
        - spatial indexing
        - temporal data retrieval
        - weather state construction
    """

    def __init__(self, bridge):
        self.bridge = bridge

        self._grid_index = None
        self._index_reader = None

    def open(self):
        """Open the weather sources and initialize indexing."""

        self.bridge.open()

        try:
            self._index_reader = self.bridge.get_reader(
                "temperature"
            )

            self._grid_index = WeatherGridIndex(
                self._index_reader
            )

            self._grid_index.initialize()

        except Exception:
            self._grid_index = None
            self._index_reader = None
            self.bridge.close()
            raise

    def close(self):
        """Close the weather data sources."""

        self._grid_index = None
        self._index_reader = None

        self.bridge.close()

    @property
    def grid_index(self):
        """Return the underlying WeatherGridIndex."""

        if self._grid_index is None:
            raise RuntimeError(
                "WeatherDataset is not open."
            )

        return self._grid_index

    def get_value(
        self,
        variable,
        time,
        latitude,
        longitude,
    ):
        """Get one converted weather value at a location and time."""

        self._ensure_open()

        if variable not in WEATHER_VARIABLES:
            raise ValueError(
                f"Unsupported weather variable: {variable}"
            )

        definition = WEATHER_VARIABLES[variable]

        result = self.bridge.get_value(
            variable,
            time,
            latitude,
            longitude,
        )

        value = definition.convert(result["value"])

        return WeatherValue(
            variable=definition.name,
            time=result["time"],
            requested_latitude=result["requested_latitude"],
            requested_longitude=result["requested_longitude"],
            latitude=result["latitude"],
            longitude=result["longitude"],
            value=float(value),
            unit=definition.output_unit,
        )

    def get_field(
        self,
        variable,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """Get a converted weather field over a spatial region."""

        self._ensure_open()

        if variable not in WEATHER_VARIABLES:
            raise ValueError(
                f"Unsupported weather variable: {variable}"
            )

        definition = WEATHER_VARIABLES[variable]

        data = self.bridge.get_region(
            variable,
            time,
            min_latitude,
            max_latitude,
            min_longitude,
            max_longitude,
        )

        data = definition.convert(data)

        return WeatherField(
            variable=definition.name,
            time=str(data.valid_time.values),
            latitudes=data.latitude.values,
            longitudes=data.longitude.values,
            data=data,
            unit=definition.output_unit,
        )

        
    def get_region_statistics(
        self,
        variable,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """Calculate descriptive statistics for a regional weather field."""

        weather_field = self.get_field(
            variable=variable,
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )

        result = RegionalWeatherStatistics.calculate(weather_field)

        result["region"] = {
            "min_latitude": float(min_latitude),
            "max_latitude": float(max_latitude),
            "min_longitude": float(min_longitude),
            "max_longitude": float(max_longitude),
        }

        return result

    

    def get_time_series(
        self,
        variable,
        start_time,
        end_time,
        latitude,
        longitude,
        time_step=1,
    ):
        """
        Get a converted weather time series at one location.

        Parameters:
            variable: Application-level variable name.
            start_time: Inclusive start of the requested period.
            end_time: Inclusive end of the requested period.
            latitude: Requested latitude.
            longitude: Requested longitude.
            time_step: Return every Nth available ERA5 timestamp.

        Returns:
            JSON-safe dictionary with timestamps, converted values,
            units, and the selected ERA5 grid coordinates.
        """

        self._ensure_open()

        if variable not in WEATHER_VARIABLES:
            raise ValueError(
                f"Unsupported weather variable: {variable}"
            )

        definition = WEATHER_VARIABLES[variable]

        result = self.bridge.get_time_series(
            variable_name=variable,
            start_time=start_time,
            end_time=end_time,
            latitude=latitude,
            longitude=longitude,
            time_step=time_step,
        )

        # Apply the same conversion used by get_value() and
        # get_field(), preserving None for missing samples.
        converted_values = []

        for value in result["values"]:
            if value is None:
                converted_values.append(None)
                continue

            converted = definition.convert(value)
            converted_values.append(float(converted))

        return {
            "variable": definition.name,
            "unit": definition.output_unit,
            "start_time": result["start_time"],
            "end_time": result["end_time"],
            "requested_latitude": result["requested_latitude"],
            "requested_longitude": result["requested_longitude"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "time_step": result["time_step"],
            "count": len(converted_values),
            "timestamps": result["timestamps"],
            "values": converted_values,
        }

    def get_state(
        self,
        time,
        latitude,
        longitude,
    ):
        """Get the complete atmospheric state at a location and time."""

        values = {}

        for variable_name in WEATHER_VARIABLES:
            values[variable_name] = self.get_value(
                variable=variable_name,
                time=time,
                latitude=latitude,
                longitude=longitude,
            )

        return WeatherState(
            time=time,
            latitude=latitude,
            longitude=longitude,
            temperature=values["temperature"].value,
            dewpoint=values["dewpoint"].value,
            mean_sea_level_pressure=(
                values["mean_sea_level_pressure"].value
            ),
            surface_pressure=values["surface_pressure"].value,
            wind_u=values["wind_u"].value,
            wind_v=values["wind_v"].value,
            total_precipitation=(
                values["total_precipitation"].value
            ),
        )

    def get_grid_index(
        self,
        time,
        latitude,
        longitude,
    ):
        """Resolve a coordinate and timestamp to a grid location."""

        self._ensure_open()

        return self._grid_index.get_grid_index(
            time=time,
            latitude=latitude,
            longitude=longitude,
        )

    def get_temperature(
        self,
        time,
        latitude,
        longitude,
    ):
        """Get temperature at a location and time."""

        return self.get_value(
            variable="temperature",
            time=time,
            latitude=latitude,
            longitude=longitude,
        )

    def get_temperature_field(
        self,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """Compatibility helper for temperature fields."""

        return self.get_field(
            variable="temperature",
            time=time,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )

    
    def get_metadata(self):
        """Return metadata for the currently open weather datasets."""

        self._ensure_open()

        # Use the existing temperature reader for the shared
        # global latitude/longitude grid and time coordinate.
        reader = self.bridge.get_reader("temperature")

        latitudes = np.asarray(
            reader.get_latitudes().values
        )
        longitudes = np.asarray(
            reader.get_longitudes().values
        )
        times = np.asarray(
            reader.get_times().values
        )

        if times.size == 0:
            raise RuntimeError(
                "The ERA5 dataset contains no timestamps."
            )

        # Calculate the nominal interval when the time axis
        # contains at least two timestamps.
        interval_hours = None

        if times.size >= 2:
            differences = np.diff(
                times.astype("datetime64[ns]")
            ).astype("timedelta64[s]").astype(np.int64)

            positive_differences = differences[
                differences > 0
            ]

            if positive_differences.size:
                interval_hours = (
                    float(np.median(positive_differences))
                    / 3600.0
                )

        variables = []

        for variable_id, definition in WEATHER_VARIABLES.items():
            source_reader = self.bridge.get_reader(variable_id)

            variables.append({
                "id": variable_id,
                "name": definition.name,
                "unit": definition.output_unit,
                "source_variable": (
                    self.bridge._get_source_variable(variable_id)
                ),
                "source_file": source_reader.file_path.name,
            })

        latitude_step = None
        longitude_step = None

        if latitudes.size >= 2:
            latitude_step = float(
                np.median(np.abs(np.diff(latitudes)))
            )

        if longitudes.size >= 2:
            longitude_step = float(
                np.median(np.abs(np.diff(longitudes)))
            )

        return {
            "dataset": "ERA5",
            "variables": variables,
            "grid": {
                "type": "regular_latitude_longitude",
                "latitude_dimension": "latitude",
                "longitude_dimension": "longitude",
                "height": int(latitudes.size),
                "width": int(longitudes.size),
                "point_count": int(
                    latitudes.size * longitudes.size
                ),
                "latitude_min": float(np.min(latitudes)),
                "latitude_max": float(np.max(latitudes)),
                "longitude_min": float(np.min(longitudes)),
                "longitude_max": float(np.max(longitudes)),
                "latitude_spacing_degrees": latitude_step,
                "longitude_spacing_degrees": longitude_step,
                "latitude_order": (
                    "north_to_south"
                    if latitudes.size < 2
                    or latitudes[0] > latitudes[-1]
                    else "south_to_north"
                ),
                "longitude_convention": (
                    "0_to_360"
                    if np.min(longitudes) >= 0
                    and np.max(longitudes) > 180
                    else "minus180_to_180"
                ),
            },
            "time": {
                "dimension": "valid_time",
                "count": int(times.size),
                "first": str(times[0]),
                "last": str(times[-1]),
                "nominal_interval_hours": interval_hours,
            },
        }
    

    def _ensure_open(self):
        """Ensure the dataset is initialized."""

        if self._grid_index is None:
            raise RuntimeError(
                "WeatherDataset is not open. Call open() first."
            )

    def get_available_times(self, start_time, end_time, interval_hours=6):
        """Return available ERA5 timestamps in an inclusive time range."""

        self._ensure_open()

        if start_time > end_time:
            raise ValueError("start_time must not exceed end_time.")

        if interval_hours <= 0:
            raise ValueError("interval_hours must be positive.")

        reader = self.bridge.get_reader("temperature")

        times = np.asarray(
            reader.get_times().values
        ).astype("datetime64[ns]")

        start = np.datetime64(start_time, "ns")
        end = np.datetime64(end_time, "ns")

        selected = times[(times >= start) & (times <= end)]

        if selected.size == 0:
            raise ValueError(
                "No ERA5 timestamps exist in the requested analysis range."
            )

        # Select every Nth available timestamp, rather than constructing
        # timestamps that might not exist in the dataset.
        interval_seconds = interval_hours * 3600

        selected_seconds = (
            selected.astype("datetime64[s]").astype(np.int64)
        )

        if selected.size > 1:
            differences = np.diff(selected_seconds)
            nominal_seconds = int(round(np.median(differences)))

            if interval_seconds % nominal_seconds != 0:
                raise ValueError(
                    f"Requested interval of {interval_hours} hours "
                    "does not align with the dataset's nominal cadence."
                )

            stride = interval_seconds // nominal_seconds

            if stride < 1:
                raise ValueError(
                    "Requested interval is shorter than the dataset cadence."
                )

            selected = selected[::stride]

        return [
            np.datetime_as_string(timestamp, unit="s")
            for timestamp in selected
        ]
