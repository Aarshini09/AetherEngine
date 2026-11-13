from pathlib import Path
import json

from weather.weather_data_bridge import WeatherDataBridge
from weather.weather_dataset import WeatherDataset


DATA_ROOT = Path(r"D:\WeatherData\ERA5\raw")


def main():
    dataset = WeatherDataset(
        WeatherDataBridge(DATA_ROOT)
    )

    try:
        dataset.open()
        print("[Test] WeatherDataset opened.")

        variables = [
            "temperature",
            "dewpoint",
            "wind_u",
        ]

        for variable in variables:
            result = dataset.get_time_series(
                variable=variable,
                start_time="2015-01-01T00:00",
                end_time="2015-01-02T00:00",
                latitude=21.0,
                longitude=79.0,
            )

            assert result["count"] > 0
            assert len(result["timestamps"]) == result["count"]
            assert len(result["values"]) == result["count"]

            json.dumps(result, allow_nan=False)

            print(f"\nVariable: {result['variable']}")
            print(f"Unit: {result['unit']}")
            print(f"Samples: {result['count']}")
            print(f"First values: {result['values'][:3]}")
            print("Request passed.")

        temperature = dataset.get_time_series(
            variable="temperature",
            start_time="2015-01-01T00:00",
            end_time="2015-01-02T00:00",
            latitude=21.0,
            longitude=79.0,
        )

        # Verify the output is in Celsius, not raw Kelvin.
        assert temperature["unit"] == "°C"
        assert (
            temperature["values"][0] < 100
            or temperature["values"][0] is None
        )

        print("\nUnit conversion checks passed.")

    finally:
        dataset.close()
        print("[Test] WeatherDataset closed.")


if __name__ == "__main__":
    main()
