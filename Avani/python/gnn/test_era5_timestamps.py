
from application.avani_application import AvaniApplication

app = AvaniApplication(r"D:\WeatherData\ERA5\raw")

try:
    app.initialize()

    dataset = app.weather_dataset
    metadata = dataset.get_metadata()

    print("Dataset:", metadata["dataset"])
    print("Time metadata:", metadata["time"])

    times = dataset.get_available_times(
        start_time="2019-07-15T00:00:00",
        end_time="2019-07-17T00:00:00",
        interval_hours=6,
    )

    print("Selected timestamps:", len(times))
    for timestamp in times:
        print(timestamp)

finally:
    app.shutdown()
