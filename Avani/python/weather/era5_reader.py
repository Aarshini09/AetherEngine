from pathlib import Path

import numpy as np
import xarray as xr


class ERA5Reader:
    """
    Reader for ERA5 NetCDF datasets.

    The reader keeps the dataset lazy. It does not load the
    complete weather field into RAM.

    Responsibilities:
    - Open and close NetCDF datasets.
    - Retrieve available times and coordinates.
    - Read individual weather values.
    - Retrieve geographic regions on demand.
    - Handle longitude conventions and coordinate ordering.
    """

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.dataset = None

    def open(self):
        """Open the ERA5 NetCDF dataset."""

        if self.dataset is not None:
            return

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"ERA5 file not found: {self.file_path}"
            )

        self.dataset = xr.open_dataset(
            self.file_path,
            engine="netcdf4",
        )

    def close(self):
        """Close the underlying dataset."""

        if self.dataset is not None:
            self.dataset.close()
            self.dataset = None

    def get_times(self):
        """Return the available valid times."""

        self._ensure_open()
        return self.dataset["valid_time"]

    def get_latitudes(self):
        """Return the latitude coordinate."""

        self._ensure_open()
        return self.dataset["latitude"]

    def get_longitudes(self):
        """Return the longitude coordinate."""

        self._ensure_open()
        return self.dataset["longitude"]

    def get_variable(self, variable_name):
        """
        Return an ERA5 variable as an xarray DataArray.

        Example:
            get_variable("t2m")
        """

        self._ensure_open()
        self._validate_variable(variable_name)

        return self.dataset[variable_name]

    def get_value(
        self,
        variable_name,
        time,
        latitude,
        longitude,
    ):
        """
        Get one weather value at a specific time and location.

        The nearest ERA5 grid point is used.

        Longitude input uses the GIS convention [-180, 180].
        The returned longitude is the original ERA5 coordinate.
        """

        self._ensure_open()
        self._validate_variable(variable_name)

        if not -90.0 <= latitude <= 90.0:
            raise ValueError(
                "Latitude must be between -90 and 90."
            )

        if not -180.0 <= longitude <= 180.0:
            raise ValueError(
                "Longitude must be between -180 and 180."
            )

        era5_longitude = longitude % 360.0

        data = self.dataset[variable_name].sel(
            valid_time=time,
            latitude=latitude,
            longitude=era5_longitude,
            method="nearest",
        )

        value = float(data.item())

        selected_longitude = float(data["longitude"].values)

        # Return the selected longitude in the conventional
        # GIS range while preserving the source coordinate
        # internally in the dataset.
        display_longitude = (
            (selected_longitude + 180.0) % 360.0
        ) - 180.0

        return {
            "variable": variable_name,
            "time": str(data["valid_time"].values),
            "requested_latitude": float(latitude),
            "requested_longitude": float(longitude),
            "latitude": float(data["latitude"].values),
            "longitude": display_longitude,
            "value": value,
        }

    def get_region(
        self,
        variable_name,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """
        Get a spatial subset of an ERA5 variable at one time.

        The returned xarray DataArray remains lazy until its
        values are accessed.

        Latitude bounds use the usual south-to-north convention.

        Longitude bounds use [-180, 180].

        If min_longitude > max_longitude, the requested region
        crosses the antimeridian.

        Examples:
            (-90, 90, -180, 180): entire globe
            (15, 25, 70, 85): regional request
            (-20, 20, 170, -170): antimeridian crossing
        """

        self._ensure_open()
        self._validate_variable(variable_name)

        self._validate_region(
            min_latitude,
            max_latitude,
            min_longitude,
            max_longitude,
        )

        variable = self.dataset[variable_name]

        # Select time first, leaving a spatial DataArray.
        data = variable.sel(
            valid_time=np.datetime64(time),
            method="nearest"
        )

        latitudes = np.asarray(data["latitude"].values)
        longitudes = np.asarray(data["longitude"].values)

        # Select latitude independently of coordinate ordering.
        latitude_mask = (
            (latitudes >= min_latitude)
            & (latitudes <= max_latitude)
        )

        # Normalize source longitudes to [-180, 180).
        normalized_longitudes = (
            (longitudes + 180.0) % 360.0
        ) - 180.0

        # A request with bounds -180 and 180 represents the
        # complete globe, including all source longitude cells.
        if min_longitude == -180.0 and max_longitude == 180.0:
            longitude_mask = np.ones(
                len(longitudes),
                dtype=bool,
            )
        elif min_longitude <= max_longitude:
            longitude_mask = (
                (normalized_longitudes >= min_longitude)
                & (normalized_longitudes <= max_longitude)
            )
        else:
            # The region crosses the antimeridian.
            longitude_mask = (
                (normalized_longitudes >= min_longitude)
                | (normalized_longitudes <= max_longitude)
            )

        latitude_indices = np.flatnonzero(latitude_mask)
        longitude_indices = np.flatnonzero(longitude_mask)

        if latitude_indices.size == 0:
            raise ValueError(
                "The requested latitude range contains "
                "no ERA5 grid points."
            )

        if longitude_indices.size == 0:
            raise ValueError(
                "The requested longitude range contains "
                "no ERA5 grid points."
            )

        # Index-based selection works with ascending or
        # descending coordinates and preserves laziness.
        region = data.isel(
            latitude=latitude_indices,
            longitude=longitude_indices,
        )

        return region

    @staticmethod
    def _validate_region(
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """Validate geographic bounds."""

        if not -90.0 <= min_latitude <= 90.0:
            raise ValueError(
                "min_latitude must be between -90 and 90."
            )

        if not -90.0 <= max_latitude <= 90.0:
            raise ValueError(
                "max_latitude must be between -90 and 90."
            )

        if min_latitude > max_latitude:
            raise ValueError(
                "min_latitude must not exceed max_latitude."
            )

        if not -180.0 <= min_longitude <= 180.0:
            raise ValueError(
                "min_longitude must be between -180 and 180."
            )

        if not -180.0 <= max_longitude <= 180.0:
            raise ValueError(
                "max_longitude must be between -180 and 180."
            )

    def _validate_variable(self, variable_name):
        """Ensure the requested variable exists."""

        if variable_name not in self.dataset.data_vars:
            raise KeyError(
                f"Variable '{variable_name}' was not found "
                f"in {self.file_path.name}."
            )
   
    def get_time_series(
        self,
        variable_name,
        start_time,
        end_time,
        latitude,
        longitude,
        time_step=1,
    ):
        """
        Get a weather time series at the nearest ERA5 grid point.

        Parameters:
            variable_name: Internal ERA5 variable, e.g. "t2m".
            start_time: Beginning of the requested time range.
            end_time: End of the requested time range.
            latitude: Requested latitude in [-90, 90].
            longitude: Requested longitude in [-180, 180].
            time_step: Return every Nth available time point.

        Returns:
            A JSON-safe dictionary containing timestamps,
            values, units-independent source metadata, and
            the selected ERA5 grid coordinates.

        The dataset remains open. Only the requested time series
        is loaded into memory.
        """

        self._ensure_open()
        self._validate_variable(variable_name)

        if not -90.0 <= latitude <= 90.0:
            raise ValueError(
                "Latitude must be between -90 and 90."
            )

        if not -180.0 <= longitude <= 180.0:
            raise ValueError(
                "Longitude must be between -180 and 180."
            )

        if (
            isinstance(time_step, bool)
            or not isinstance(time_step, (int, np.integer))
            or time_step < 1
        ):
            raise ValueError(
                "time_step must be a positive integer."
            )

        if start_time > end_time:
            raise ValueError(
                "start_time must not be later than end_time."
            )

        # ERA5 commonly stores longitude in [0, 360).
        era5_longitude = longitude % 360.0

        # Select the nearest grid point first, then the time range.
        point = self.dataset[variable_name].sel(
            latitude=latitude,
            longitude=era5_longitude,
            method="nearest",
        )

        series = point.sel(
            valid_time=slice(start_time, end_time)
        )

        # Apply time sampling without loading the entire range.
        series = series.isel(
            valid_time=slice(None, None, int(time_step))
        )

        if series.sizes.get("valid_time", 0) == 0:
            raise ValueError(
                "No ERA5 timestamps were found in the requested "
                "time range."
            )

        # Materialize only the selected point and time range.
        timestamps = series["valid_time"].values
        raw_values = np.asarray(series.values).reshape(-1)

        values = []
        for value in raw_values:
            numeric_value = float(value)
            values.append(
                numeric_value
                if np.isfinite(numeric_value)
                else None
            )

        selected_latitude = float(
            series["latitude"].values
        )
        selected_longitude = float(
            series["longitude"].values
        )

        # Normalize the reported longitude to [-180, 180).
        selected_longitude = (
            (selected_longitude + 180.0) % 360.0
        ) - 180.0

        return {
            "variable": variable_name,
            "start_time": str(timestamps[0]),
            "end_time": str(timestamps[-1]),
            "requested_latitude": float(latitude),
            "requested_longitude": float(longitude),
            "latitude": selected_latitude,
            "longitude": selected_longitude,
            "time_step": int(time_step),
            "count": len(values),
            "timestamps": [
                str(timestamp) for timestamp in timestamps
            ],
            "values": values,
        }

    def _ensure_open(self):
        """Make sure the dataset is open."""

        if self.dataset is None:
            raise RuntimeError(
                "ERA5 dataset is not open. Call open() first."
            )
