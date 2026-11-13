from pathlib import Path

import numpy as np
import json
from application.analysis_scope import AnalysisScope
from application.avani_application import AvaniApplication
from application.application_loop import ApplicationLoop
from visualization.global_visualization_builder import (
    GlobalVisualizationBuilder
)

def main():
    weather_data_root = Path(
        r"D:\WeatherData\ERA5\raw"
    )

    application = AvaniApplication(
        weather_data_root=weather_data_root
    )

    application_loop = ApplicationLoop(
        application=application,
        tick_rate=20.0
    )

    try:
        application.initialize()

        global_visualization_output = Path(
            r"C:\Users\Ajivak\Desktop\AI_V1\Avani"
            r"\public\data\visualization"
            r"\global_temperature.json"
        )

        builder = GlobalVisualizationBuilder(
            source_path=None,
            output_path=global_visualization_output,
            variable="temperature",
            spatial_step=8,
            weather_dataset=application.weather_dataset,
        )

        builder.build(
            start_time=np.datetime64("2015-01-01T00:00"),
            end_time=np.datetime64("2015-01-02T00:00"),
        )        

        analysis_scope = AnalysisScope(
            min_latitude=20.0,
            max_latitude=21.0,
            min_longitude=78.0,
            max_longitude=80.0,
            variable="temperature",
            start_time=np.datetime64(
                "2015-01-01T00:00"
            ),
            end_time=np.datetime64(
                "2019-12-31T18:00"
            )
        )

        application.configure_analysis(
            analysis_scope
        )

        application.run_analysis(
            time=np.datetime64(
                "2015-01-01T00:00"
            )
        )
        
        analysis_times = np.arange(
            np.datetime64("2015-01-01T00:00"),
            np.datetime64("2015-01-02T00:00"),
            np.timedelta64(6, "h")
        )

        temporal_result = application.run_analysis_range(
            analysis_times
        )

        visualization_timeline = (
            temporal_result["visualization_timeline"]
        )

        timeline_data = visualization_timeline.to_dict()

        print()
        print("========================================")
        print("     VISUALIZATION SERIALIZATION TEST")
        print("========================================")
        print()
        print(
            f"Variable: "
            f"{timeline_data['variable']}"
        )
        print(
            f"Frames: "
            f"{timeline_data['frame_count']}"
        )
        print(
            f"Start: "
            f"{timeline_data['start_time']}"
        )
        print(
            f"End: "
            f"{timeline_data['end_time']}"
        )
        print(
            f"Tracks: "
            f"{len(timeline_data['tracks'])}"
        )
        print(
            f"Events: "
            f"{len(timeline_data['events'])}"
        )

        for frame in timeline_data["frames"]:
            print(
                f"[Frame] "
                f"time={frame['time']}, "
                f"anomalies={len(frame['anomalies'])}, "
                f"regions={len(frame['regions'])}"
            )

        print()

        json_text = json.dumps(
            timeline_data,
            indent=2
        )
     
        visualization_output_path = Path(
            r"C:\Users\Ajivak\Desktop\AI_V1\Avani\public\data\visualization\timeline.json"
        )

        visualization_output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        visualization_output_path.write_text(
            json_text,
            encoding="utf-8"
        )

        print(
            "[Visualization] JSON file written:"
        )
        print(
            f"[Visualization] "
            f"{visualization_output_path}"
        )

        print()
        print(
            "[Visualization] JSON serialization successful."
        )
        print(
            f"[Visualization] JSON size: "
            f"{len(json_text)} characters"
        )


        application.run(
            application_loop
        )

    except KeyboardInterrupt:
        print()
        print(
            "[Avani] Shutdown requested "
            "from keyboard."
        )

    finally:
        application.shutdown()


if __name__ == "__main__":
    main()