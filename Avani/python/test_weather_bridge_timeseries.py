from pathlib import Path
import json

from weather.weather_data_bridge import WeatherDataBridge


DATA_ROOT = Path(r"D:\WeatherData\ERA5\raw")


def main():
    bridge = WeatherDataBridge(DATA_ROOT)

    try:
        bridge.open()
        print("[Test] WeatherDataBridge opened.")

        variables = [
            "temperature",
            "dewpoint",
            "wind_u",
        ]

        for variable in variables:
            result = bridge.get_time_series(
                variable_name=variable,
                start_time="2015-01-01T00:00",
                end_time="2015-01-02T00:00",
                latitude=21.0,
                longitude=79.0,
                time_step=1,
            )

            assert result["count"] > 0
            assert len(result["timestamps"]) == result["count"]
            assert len(result["values"]) == result["count"]

            json.dumps(result, allow_nan=False)

            print(f"\nVariable: {variable}")
            print(f"Samples: {result['count']}")
            print(f"Grid point: {result['latitude']}, "
                  f"{result['longitude']}")
            print(f"First values: {result['values'][:3]}")
            print("Request passed.")

    finally:
        bridge.close()
        print("\n[Test] WeatherDataBridge closed.")


if __name__ == "__main__":
    main()
