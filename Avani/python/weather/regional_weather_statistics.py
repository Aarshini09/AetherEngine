
import numpy as np


class RegionalWeatherStatistics:
    """
    Calculate descriptive statistics for one spatial weather field.

    The input field must already have its output units applied.
    Geographic cell-area weights are approximated using
    cosine(latitude), appropriate for a regular latitude/longitude
    grid when cells have equal angular spacing.
    """

    @staticmethod
    def calculate(weather_field):
        data = weather_field.data

        # Materialize only the selected regional field.
        values = np.asarray(data.values, dtype=np.float64)

        if values.ndim != 2:
            raise ValueError(
                "Expected a 2D regional field "
                "with latitude and longitude dimensions."
            )

        latitudes = np.asarray(
            weather_field.latitudes, dtype=np.float64
        )
        longitudes = np.asarray(
            weather_field.longitudes, dtype=np.float64
        )

        if values.shape != (latitudes.size, longitudes.size):
            raise ValueError(
                "Regional field dimensions do not match "
                "the latitude and longitude coordinates."
            )

        # Exclude NaN and infinite values from statistics.
        valid_mask = np.isfinite(values)
        valid_values = values[valid_mask]

        if valid_values.size == 0:
            raise ValueError(
                "The selected region contains no valid weather values."
            )

        # Each latitude row receives a cosine(latitude) weight.
        # Longitude spacing is uniform for the ERA5 grid.
        latitude_weights = np.cos(np.deg2rad(latitudes))
        latitude_weights = np.clip(latitude_weights, 0.0, None)

        weights = np.broadcast_to(
            latitude_weights[:, np.newaxis],
            values.shape,
        )

        valid_weights = weights[valid_mask]
        weight_sum = float(np.sum(valid_weights))

        if weight_sum <= 0:
            raise ValueError(
                "Cannot calculate an area-weighted mean "
                "for the selected grid cells."
            )

        weighted_mean = float(
            np.sum(valid_values * valid_weights) / weight_sum
        )

        minimum = float(np.min(valid_values))
        maximum = float(np.max(valid_values))

        min_index = np.argwhere(
            valid_mask & (values == minimum)
        )[0]
        max_index = np.argwhere(
            valid_mask & (values == maximum)
        )[0]

        # Percentiles describe the distribution of grid-cell values.
        percentiles = np.percentile(
            valid_values, [10, 25, 50, 75, 90]
        )

        return {
            "variable": weather_field.variable,
            "time": str(weather_field.time),
            "unit": weather_field.unit,
            "grid": {
                "latitude_count": int(latitudes.size),
                "longitude_count": int(longitudes.size),
                "total_cell_count": int(values.size),
                "valid_cell_count": int(valid_values.size),
                "missing_cell_count": int(
                    values.size - valid_values.size
                ),
            },
            "statistics": {
                "area_weighted_mean": weighted_mean,
                "minimum": minimum,
                "maximum": maximum,
                "standard_deviation": float(
                    np.std(valid_values)
                ),
                "percentiles": {
                    "p10": float(percentiles[0]),
                    "p25": float(percentiles[1]),
                    "p50": float(percentiles[2]),
                    "p75": float(percentiles[3]),
                    "p90": float(percentiles[4]),
                },
            },
            "extrema_locations": {
                "minimum": {
                    "latitude": float(latitudes[min_index[0]]),
                    "longitude": float(longitudes[min_index[1]]),
                },
                "maximum": {
                    "latitude": float(latitudes[max_index[0]]),
                    "longitude": float(longitudes[max_index[1]]),
                },
            },
        }
