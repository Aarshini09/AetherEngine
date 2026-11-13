from pathlib import Path

import xarray as xr


FILE_PATH = Path(
    r"D:\WeatherData\ERA5\raw\dewpoint_pressure_2015_2019.nc"
)


print("ERA5 FILE")
print("---------")
print("Path:", FILE_PATH)
print("Size:", f"{FILE_PATH.stat().st_size / (1024 ** 3):.2f} GB")


print()
print("Opening dataset...")


dataset = xr.open_dataset(
    FILE_PATH,
    engine="netcdf4"
)


print()
print("DATASET")
print("-------")
print(dataset)


print()
print("DIMENSIONS")
print("----------")

for name, size in dataset.sizes.items():
    print(f"{name}: {size}")


print()
print("COORDINATES")
print("-----------")

for name in dataset.coords:
    coordinate = dataset.coords[name]

    print()
    print(name)
    print("  dimensions:", coordinate.dims)
    print("  shape:", coordinate.shape)

    if coordinate.size <= 10:
        print("  values:", coordinate.values)
    else:
        print("  first:", coordinate.values[:3])
        print("  last:", coordinate.values[-3:])


print()
print("DATA VARIABLES")
print("--------------")

for name in dataset.data_vars:
    variable = dataset[name]

    print()
    print(name)
    print("  dimensions:", variable.dims)
    print("  shape:", variable.shape)
    print("  dtype:", variable.dtype)

    print("  attributes:")

    for key, value in variable.attrs.items():
        print(f"    {key}: {value}")


print()
print("GLOBAL ATTRIBUTES")
print("-----------------")

for key, value in dataset.attrs.items():
    print(f"{key}: {value}")


dataset.close()

print()
print("Dataset closed.")