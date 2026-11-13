from pathlib import Path
import numpy as np

from application.avani_application import AvaniApplication
from visualization.global_visualization_builder import (
    GlobalVisualizationBuilder
)


WEATHER_DATA_ROOT = Path(
    r"D:\WeatherData\ERA5\raw"
)

OUTPUT_PATH = Path(
    r"C:\Users\Ajivak\Desktop\AI_V1\Avani"
    r"\public\data\visualization"
    r"\global_temperature.json"
)

VARIABLE = "temperature"
SPATIAL_STEP = 8

START_TIME = np.datetime64("2015-01-01T00:00")
END_TIME = np.datetime64("2015-01-02T00:00")


def main():
    application = AvaniApplication(
        weather_data_root=WEATHER_DATA_ROOT
    )

    try:
        # Initialize the application and open its ERA5 dataset.
        application.initialize()

        # Reuse the dataset already owned by AvaniApplication.
        builder = GlobalVisualizationBuilder(
            source_path=None,
            output_path=OUTPUT_PATH,
            variable=VARIABLE,
            spatial_step=SPATIAL_STEP,
            weather_dataset=application.weather_dataset,
        )

        # Export the requested historical time range.
        output = builder.build(
            start_time=START_TIME,
            end_time=END_TIME,
        )

        print()
        print("[Avani] Global visualization export complete.")
        print(f"[Avani] Frames: {output['frame_count']}")
        print(f"[Avani] Output: {OUTPUT_PATH}")

    except KeyboardInterrupt:
        print()
        print("[Avani] Visualization export interrupted.")

    finally:
        # Close the dataset through its owning application.
        application.shutdown()


if __name__ == "__main__":
    main()
