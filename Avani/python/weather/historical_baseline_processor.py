import numpy as np

from weather.weather_baseline import WeatherBaseline
from weather.weather_variables import WEATHER_VARIABLES


class HistoricalBaselineProcessor:
    """
    Computes historical weather statistics from an
    ERA5Reader.

    The processor works with application-level weather
    variables.

    Example:

        temperature
            ↓
        t2m
            ↓
        Kelvin → Celsius
            ↓
        historical statistics

    Statistics are therefore stored in the application's
    output units rather than the raw ERA5 units.

    The processor performs statistical reduction directly
    on the underlying xarray DataArray.

    It does not construct WeatherState objects and does
    not build a WeatherDataGraph.
    """

    def __init__(self, reader):
        self.reader = reader

    def compute_point_baseline(
        self,
        variable_name,
        latitude,
        longitude,
        start_time=None,
        end_time=None
    ):
        """
        Compute historical statistics for one application
        weather variable at one geographic location.

        Statistics are grouped by:

            month
            UTC hour

        Example:

            variable_name="temperature"

        Returns:

            {
                (month, hour): WeatherBaseline
            }
        """

        if variable_name not in WEATHER_VARIABLES:
            raise ValueError(
                f"Unsupported weather variable: "
                f"{variable_name}"
            )

        definition = WEATHER_VARIABLES[
            variable_name
        ]

        data = self.reader.get_variable(
            definition.source_name
        )

        era5_longitude = longitude % 360.0

        point = data.sel(
            latitude=latitude,
            longitude=era5_longitude,
            method="nearest"
        )

        if start_time is not None:

            point = point.sel(
                valid_time=slice(
                    start_time,
                    end_time
                )
            )

        # Convert from the ERA5 source unit into the
        # application's output unit before calculating
        # any statistics.
        point = definition.convert(
            point
        )

        times = point["valid_time"].values
        values = point.values

        groups = {}

        selected_latitude = float(
            point.latitude.values
        )

        selected_longitude = float(
            point.longitude.values
        )

        for time, value in zip(
            times,
            values
        ):

            if np.isnan(value):
                continue

            timestamp = np.datetime64(
                time
            )

            month = (
                timestamp.astype(
                    "datetime64[M]"
                ).astype(int)
                % 12
            ) + 1

            month = int(month)

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

            key = (
                month,
                hour
            )

            if key not in groups:
                groups[key] = []

            groups[key].append(
                float(value)
            )

        baselines = {}

        for (
            month,
            hour
        ), values_for_group in groups.items():

            values_array = np.asarray(
                values_for_group,
                dtype=np.float64
            )

            baseline = WeatherBaseline(
                variable=definition.name,

                unit=definition.output_unit,

                latitude=selected_latitude,
                longitude=selected_longitude,

                month=month,
                hour=hour,

                mean=float(
                    np.mean(values_array)
                ),

                standard_deviation=float(
                    np.std(values_array)
                ),

                minimum=float(
                    np.min(values_array)
                ),

                maximum=float(
                    np.max(values_array)
                ),

                sample_count=len(
                    values_array
                )
            )

            baselines[
                (month, hour)
            ] = baseline

        return baselines