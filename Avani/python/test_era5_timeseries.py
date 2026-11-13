from pathlib import Path
import json

from weather.era5_reader import ERA5Reader


FILE_PATH = Path(
    r"D:\WeatherData\ERA5\raw\temperature_2015_2019.nc"
)


def main():
    reader = ERA5Reader(FILE_PATH)

    try:
        reader.open()
        print("[Test] ERA5 dataset opened.")

        result = reader.get_time_series(
            variable_name="t2m",
            start_time="2015-01-01T00:00",
            end_time="2015-01-02T00:00",
            latitude=21.0,
            longitude=79.0,
            time_step=1,
        )

        print("\n--- Temperature Time Series ---")
        print(f"Variable: {result['variable']}")
        print(
            f"Selected grid point: "
            f"{result['latitude']}, {result['longitude']}"
        )
        print(f"Start: {result['start_time']}")
        print(f"End: {result['end_time']}")
        print(f"Returned samples: {result['count']}")
        print(f"First values: {result['values'][:5]}")

        assert result["count"] > 0
        assert (
            result["count"]
            == len(result["timestamps"])
            == len(result["values"])
        )

        # Ensure missing values are represented by None,
        # rather than non-standard JSON NaN values.
        json.dumps(result, allow_nan=False)

        print("\nTime-series request passed.")

    finally:
        reader.close()
        print("[Test] ERA5 dataset closed.")


if __name__ == "__main__":
    main()
