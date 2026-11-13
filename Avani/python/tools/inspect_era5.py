import sys
from pathlib import Path

import xarray as xr


def inspect_era5(file_path):
    path = Path(file_path)

    if not path.exists():
        print(f"ERROR: File not found:")
        print(path)
        return

    print("=" * 70)
    print("ERA5 FILE")
    print("=" * 70)

    print(f"Path: {path}")
    print(f"Size: {path.stat().st_size / (1024 ** 3):.2f} GB")

    print("\nOpening NetCDF dataset...")

    dataset = xr.open_dataset(
        path,
        engine="netcdf4"
    )

    print("\n" + "=" * 70)
    print("DATASET")
    print("=" * 70)

    print(dataset)

    print("\n" + "=" * 70)
    print("DIMENSIONS")
    print("=" * 70)

    for name, size in dataset.sizes.items():
        print(f"{name}: {size}")

    print("\n" + "=" * 70)
    print("COORDINATES")
    print("=" * 70)

    for name, coordinate in dataset.coords.items():
        print(f"\n{name}")
        print(f"  dimensions: {coordinate.dims}")
        print(f"  shape:      {coordinate.shape}")
        print(f"  dtype:      {coordinate.dtype}")

    print("\n" + "=" * 70)
    print("DATA VARIABLES")
    print("=" * 70)

    for name, variable in dataset.data_vars.items():
        print(f"\n{name}")
        print(f"  dimensions: {variable.dims}")
        print(f"  shape:      {variable.shape}")
        print(f"  dtype:      {variable.dtype}")

        print("  attributes:")

        for key, value in variable.attrs.items():
            print(f"    {key}: {value}")

    print("\n" + "=" * 70)
    print("GLOBAL ATTRIBUTES")
    print("=" * 70)

    for key, value in dataset.attrs.items():
        print(f"{key}: {value}")

    dataset.close()

    print("\nInspection complete.")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python tools\\inspect_era5.py <path-to-file>")
        sys.exit(1)

    inspect_era5(sys.argv[1])