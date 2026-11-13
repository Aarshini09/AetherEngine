from pathlib import Path
import json

from application.avani_application import AvaniApplication


DATA_ROOT = Path(r"D:\WeatherData\ERA5\raw")


def main():
    app = AvaniApplication(DATA_ROOT)

    try:
        app.initialize()

        result = app.get_weather_time_series(
            variable="temperature",
            start_time="2015-01-01T00:00",
            end_time="2015-01-02T00:00",
            latitude=21.0,
            longitude=79.0,
        )

        print("\n--- Application Time Series ---")
        print(f"Variable: {result['variable']}")
        print(f"Unit: {result['unit']}")
        print(f"Samples: {result['count']}")
        print(f"Selected grid point: "
              f"{result['latitude']}, {result['longitude']}")
        print(f"First values: {result['values'][:3]}")

        # Confirm the result can be serialized for an API/frontend.
        json.dumps(result, allow_nan=False)

        assert result["count"] > 0
        assert result["unit"] == "°C"
        assert len(result["timestamps"]) == result["count"]
        assert len(result["values"]) == result["count"]

        print("\nApplication time-series test passed.")

    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
