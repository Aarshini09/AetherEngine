from pathlib import Path

import json
import numpy as np

from application.avani_application import AvaniApplication


WEATHER_DATA_ROOT = Path(r"D:\WeatherData\ERA5\raw")


def main():
    application = AvaniApplication(
        weather_data_root=WEATHER_DATA_ROOT
    )

    try:
        application.initialize()

        requests = [
            ("temperature", np.datetime64("2015-01-01T12:00")),
            ("dewpoint", np.datetime64("2015-01-01T12:00")),
            ("wind_u", np.datetime64("2015-01-01T12:00")),
        ]

        for variable, timestamp in requests:
            frame = application.get_weather_frame(
                variable=variable,
                time=timestamp,
                min_latitude=15.0,
                max_latitude=25.0,
                min_longitude=70.0,
                max_longitude=85.0,
                max_rows=32,
                max_columns=32,
            )

            print()
            print(f"Variable: {frame['variable']}")
            print(f"Time: {frame['time']}")
            print(f"Unit: {frame['unit']}")
            print(
                f"Sampled dimensions: "
                f"{frame['width']} x {frame['height']}"
            )
            print(
                f"Source dimensions: "
                f"{frame['source_width']} x "
                f"{frame['source_height']}"
            )
            print(
                f"Returned values: {len(frame['values'])}"
            )

            assert len(frame["values"]) == (
                frame["width"] * frame["height"]
            )

            # Confirm that the returned frame can be serialized
            # without NaN or Infinity values.
            json.dumps(frame, allow_nan=False)

            print("Request passed.")

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()
