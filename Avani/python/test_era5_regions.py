from pathlib import Path

import numpy as np

from weather.era5_reader import ERA5Reader


FILE_PATH = Path(
    r"D:\WeatherData\ERA5\raw\temperature_2015_2019.nc"
)

TEST_TIME = np.datetime64("2015-01-01T12:00")


def main():
    reader = ERA5Reader(FILE_PATH)

    tests = [
        ("Regional", 15, 25, 70, 85),
        ("Full globe", -90, 90, -180, 180),
        ("Antimeridian", -20, 20, 170, -170),
    ]

    try:
        reader.open()
        print("[Test] ERA5 dataset opened.")

        for name, min_lat, max_lat, min_lon, max_lon in tests:
            field = reader.get_region(
                variable_name="t2m",
                time=TEST_TIME,
                min_latitude=min_lat,
                max_latitude=max_lat,
                min_longitude=min_lon,
                max_longitude=max_lon,
            )

            print(f"\n--- {name} ---")
            print(f"Shape: {field.shape}")
            print(f"Latitude points: {field.sizes['latitude']}")
            print(f"Longitude points: {field.sizes['longitude']}")

            assert field.ndim == 2, (
                f"{name}: expected a 2D field, got {field.ndim}D."
            )
            assert field.size > 0, (
                f"{name}: the returned region is empty."
            )

        print("\nAll geographic extraction tests passed.")

    finally:
        reader.close()
        print("[Test] ERA5 dataset closed.")


if __name__ == "__main__":
    main()
