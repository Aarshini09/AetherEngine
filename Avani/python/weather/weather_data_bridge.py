from pathlib import Path

from weather.era5_reader import ERA5Reader


class WeatherDataBridge:
    """
    Connect application weather variables to their underlying
    ERA5 NetCDF files.

    Responsibilities:
        - Map application variables to source files.
        - Create and manage persistent ERA5 readers.
        - Route value, region, and time-series requests.
        - Hide ERA5 file organization from the application.
    """

    def __init__(self, raw_data_root):
        self.raw_data_root = Path(raw_data_root)

        self._readers = {}

        self._variable_sources = {
            "temperature": "temperature",
            "dewpoint": "dewpoint_pressure",
            "mean_sea_level_pressure": "dewpoint_pressure",
            "wind_u": "wind_u_surface_pressure",
            "surface_pressure": "wind_u_surface_pressure",
            "wind_v": "wind_v",
            "total_precipitation": "total_precipitation",
        }

        self._source_files = {
            "temperature": "temperature_2015_2019.nc",
            "dewpoint_pressure": "dewpoint_pressure_2015_2019.nc",
            "wind_u_surface_pressure": (
                "wind_u_surface_pressure_2015_2019.nc"
            ),
            "wind_v": "wind_v_2015_2019.nc",
            "total_precipitation": "total_precipitation_2015_2019.nc",
        }

        self._source_variables = {
            "temperature": "t2m",
            "dewpoint": "d2m",
            "mean_sea_level_pressure": "msl",
            "wind_u": "u10",
            "surface_pressure": "sp",
            "wind_v": "v10",
            "total_precipitation": "tp",
        }

    def open(self):
        """
        Open all configured ERA5 source datasets.

        If opening one dataset fails, close any readers that
        were already opened before propagating the exception.
        """

        if self._readers:
            return

        try:
            for source_name, filename in self._source_files.items():
                file_path = self.raw_data_root / filename

                reader = ERA5Reader(file_path)
                reader.open()

                self._readers[source_name] = reader

        except Exception:
            self.close()
            raise

    def close(self):
        """Close all managed ERA5 readers."""

        for reader in self._readers.values():
            reader.close()

        self._readers.clear()

    def get_value(
        self,
        variable_name,
        time,
        latitude,
        longitude,
    ):
        """Get one value for an application weather variable."""

        reader = self._get_reader(variable_name)

        return reader.get_value(
            self._get_source_variable(variable_name),
            time,
            latitude,
            longitude,
        )

    def get_region(
        self,
        variable_name,
        time,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
    ):
        """Get a spatial region for an application variable."""

        reader = self._get_reader(variable_name)

        return reader.get_region(
            self._get_source_variable(variable_name),
            time,
            min_latitude,
            max_latitude,
            min_longitude,
            max_longitude,
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
        Get a time series using an application-level variable name.

        Example:
            variable_name="temperature"

        The bridge resolves that name to the appropriate ERA5
        file and internal variable, then delegates to ERA5Reader.
        """

        reader = self._get_reader(variable_name)
        source_variable = self._get_source_variable(variable_name)

        return reader.get_time_series(
            variable_name=source_variable,
            start_time=start_time,
            end_time=end_time,
            latitude=latitude,
            longitude=longitude,
            time_step=time_step,
        )

    def get_reader(self, variable_name):
        """Return the reader responsible for a weather variable."""

        return self._get_reader(variable_name)

    def _get_reader(self, variable_name):
        """Resolve an application variable to its source reader."""

        if variable_name not in self._variable_sources:
            raise ValueError(
                f"Unsupported weather variable: {variable_name}"
            )

        source_name = self._variable_sources[variable_name]

        if source_name not in self._readers:
            raise RuntimeError(
                "WeatherDataBridge is not open. Call open() first."
            )

        return self._readers[source_name]

    def _get_source_variable(self, variable_name):
        """Resolve an application variable to its ERA5 variable name."""

        try:
            return self._source_variables[variable_name]
        except KeyError:
            raise ValueError(
                f"Unsupported weather variable: {variable_name}"
            ) from None
