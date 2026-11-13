from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
import logging

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from application.avani_application import AvaniApplication
from pydantic import BaseModel, Field, model_validator
from application.avani_application import AvaniApplication
from application.analysis_scope import AnalysisScope
# --------------------------------------------------
# Configuration
# --------------------------------------------------

WEATHER_DATA_ROOT = Path(r"D:\WeatherData\ERA5\raw")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("avani.api")


# --------------------------------------------------
# Persistent application lifecycle
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Avani backend...")

    application = AvaniApplication(WEATHER_DATA_ROOT)
    application.initialize()

    app.state.avani = application

    # Serialize access to the shared application instance.
    app.state.request_lock = Lock()

    logger.info("Avani backend is ready.")

    try:
        yield
    finally:
        logger.info("Shutting down Avani backend...")
        application.shutdown()
        logger.info("Avani backend stopped.")


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Avani Weather API",
    description=(
        "Request-driven historical ERA5 weather data "
        "and environmental analysis services."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# Development configuration for the local frontend.
# Restrict this to your actual frontend origin before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def get_application():
    application = getattr(app.state, "avani", None)

    if application is None:
        raise HTTPException(
            status_code=503,
            detail="Avani backend is not initialized.",
        )

    return application


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/api/health")
def health():
    application = get_application()

    return {
        "status": "ok",
        "application": "Avani",
        "initialized": application._initialized,
        "elapsed_time": application.elapsed_time,
        "frame_count": application.frame_count,
    }

@app.get("/api/weather/metadata")
def get_weather_metadata():
    """Return metadata describing the available ERA5 weather data."""

    application = app.state.avani

    with app.state.request_lock:
        try:
            return application.weather_dataset.get_metadata()

        except (ValueError, KeyError) as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except (RuntimeError, OSError) as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc



# --------------------------------------------------
# Weather time-series endpoint
# --------------------------------------------------

@app.get("/api/weather/time-series")
def weather_time_series(
    variable: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...),
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    time_step: int = Query(1, ge=1),
):
    application = get_application()

    try:
        with app.state.request_lock:
            result = application.get_weather_time_series(
                variable=variable,
                start_time=start_time,
                end_time=end_time,
                latitude=latitude,
                longitude=longitude,
                time_step=time_step,
            )

        return result

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, OSError) as exc:
        logger.exception("Weather time-series request failed.")

        raise HTTPException(
            status_code=500,
            detail="The weather data request could not be completed.",
        ) from exc


# --------------------------------------------------
# Spatial weather-frame endpoint
# --------------------------------------------------

@app.get("/api/weather/frame")
def weather_frame(
    variable: str = Query(...),
    time: str = Query(...),
    min_latitude: float = Query(-90.0, ge=-90.0, le=90.0),
    max_latitude: float = Query(90.0, ge=-90.0, le=90.0),
    min_longitude: float = Query(-180.0, ge=-180.0, le=180.0),
    max_longitude: float = Query(180.0, ge=-180.0, le=180.0),
    max_rows: int = Query(181, ge=1, le = 721),
    max_columns: int = Query(360, ge=1, le= 1440),
):
    application = get_application()

    if min_latitude > max_latitude:
        raise HTTPException(
            status_code=400,
            detail="min_latitude must not exceed max_latitude.",
        )

    if min_longitude > max_longitude:
        raise HTTPException(
            status_code=400,
            detail=(
                "min_longitude must not exceed max_longitude. "
                "Antimeridian-crossing requests are not supported "
                "by this endpoint yet."
            ),
        )

    try:
        with app.state.request_lock:
            result = application.get_weather_frame(
                variable=variable,
                time=time,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude,
                max_rows=max_rows,
                max_columns=max_columns,
            )

        return result

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, OSError) as exc:
        logger.exception("Weather frame request failed.")

        raise HTTPException(
            status_code=500,
            detail="The weather frame request could not be completed.",
        ) from exc


@app.get("/api/weather/region-statistics")
def weather_region_statistics(
    variable: str = Query(...),
    time: str = Query(...),
    min_latitude: float = Query(..., ge=-90.0, le=90.0),
    max_latitude: float = Query(..., ge=-90.0, le=90.0),
    min_longitude: float = Query(..., ge=-180.0, le=180.0),
    max_longitude: float = Query(..., ge=-180.0, le=180.0),
):
    application = get_application()

    if min_latitude >= max_latitude:
        raise HTTPException(
            status_code=400,
            detail="min_latitude must be less than max_latitude.",
        )

    if min_longitude >= max_longitude:
        raise HTTPException(
            status_code=400,
            detail=(
                "min_longitude must be less than max_longitude. "
                "Antimeridian-crossing requests are not supported."
            ),
        )

    try:
        with app.state.request_lock:
            result = application.weather_dataset.get_region_statistics(
                variable=variable,
                time=time,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude,
            )

        return result

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, OSError) as exc:
        logger.exception("Regional statistics request failed.")

        raise HTTPException(
            status_code=500,
            detail="Regional weather statistics could not be calculated.",
        ) from exc


class AnalysisRequest(BaseModel):
    variable: str

    min_latitude: float = Field(ge=-90, le=90)
    max_latitude: float = Field(ge=-90, le=90)
    min_longitude: float = Field(ge=-180, le=180)
    max_longitude: float = Field(ge=-180, le=180)

    baseline_start_time: datetime
    baseline_end_time: datetime

    analysis_start_time: datetime
    analysis_end_time: datetime

    interval_hours: int = Field(default=6, ge=1, le=24)

    @model_validator(mode="after")
    def validate_request(self):
        if self.min_latitude > self.max_latitude:
            raise ValueError("Minimum latitude exceeds maximum latitude.")

        if self.min_longitude > self.max_longitude:
            raise ValueError("Minimum longitude exceeds maximum longitude.")

        if self.baseline_start_time > self.baseline_end_time:
            raise ValueError("Baseline start must not exceed baseline end.")

        if self.analysis_start_time > self.analysis_end_time:
            raise ValueError("Analysis start must not exceed analysis end.")

        return self


def _select_analysis_times(
    application,
    variable,
    start_time,
    end_time,
    interval_hours,
):
    """
    Select actual dataset timestamps within the requested
    analysis interval, sampling at the requested cadence.
    """

    reader = application.weather_bridge.get_reader(variable)
    available_times = reader.get_times().values

    start = start_time.replace(tzinfo=None)
    end = end_time.replace(tzinfo=None)

    selected_times = []
    next_time = start

    for value in available_times:
        # Handles Python datetime values and common NumPy
        # datetime64 / timestamp string representations.
        timestamp = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(
                start_time.tzinfo
            ).replace(tzinfo=None) if start_time.tzinfo else (
                timestamp.astimezone().replace(tzinfo=None)
            )

        if timestamp < start or timestamp > end:
            continue

        if timestamp >= next_time:
            selected_times.append(timestamp)
            next_time = timestamp + timedelta(
                hours=interval_hours
            )

    return selected_times


@app.post("/api/analysis/run")
def run_scientific_analysis(request: AnalysisRequest):
    """
    Execute Avani's spatiotemporal scientific analysis pipeline.
    """

    application = get_application()

    try:
        with app.state.request_lock:
            # Release any previous analysis configuration.
            application.reset_analysis()

            # Configure the spatial region and baseline period.
            scope = AnalysisScope(
                min_latitude=request.min_latitude,
                max_latitude=request.max_latitude,
                min_longitude=request.min_longitude,
                max_longitude=request.max_longitude,
                variable=request.variable,
                start_time=request.baseline_start_time,
                end_time=request.baseline_end_time,
            )

            application.configure_analysis(scope)

            # Select real ERA5 timestamps in the analysis period.
            times = _select_analysis_times(
                application=application,
                variable=request.variable,
                start_time=request.analysis_start_time,
                end_time=request.analysis_end_time,
                interval_hours=request.interval_hours,
            )

            if not times:
                raise ValueError(
                    "No available ERA5 timestamps were found "
                    "in the requested analysis period."
                )

            # Run baseline -> anomalies -> regions -> tracks -> events.
            result = application.run_analysis_range(times)

            timeline = result["visualization_timeline"].to_dict()

            return {
                **timeline,
                "variable": request.variable,
                "frame_count": len(timeline.get("frames", [])),
                "track_count": len(timeline.get("tracks", [])),
                "event_count": len(timeline.get("events", [])),
                "analysis_start_time": times[0].isoformat(),
                "analysis_end_time": times[-1].isoformat(),
            }

    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except (RuntimeError, OSError) as exc:
        logger.exception("Scientific analysis failed.")

        raise HTTPException(
            status_code=500,
            detail="Scientific analysis could not be completed.",
        ) from exc
