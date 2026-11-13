import * as THREE from "three";

import { Earth } from "./earth/Earth.js";
import { Icosahedron } from "./earth/Icosahedron.js";

import { Camera } from "./camera/Camera.js";
import { Renderer } from "./renderer/Renderer.js";
import { OrbitController } from "./camera/OrbitController.js";

import { Input } from "./input/Input.js";
import { Time } from "./time/Time.js";

import {
    geoToCartesian,
    cartesianToGeo,
    raySphereIntersection
} from "./gis/CoordinateConversion.js";

import {
    IcosahedronVisualizer
} from "./renderer/IcosahedronVisualizer.js";
import {
    WeatherVisualizer
} from "./renderer/WeatherVisualizer.js";
import { WeatherField } from "./weather/WeatherField.js";
import {
    SpatialWeatherField
} from "./weather/SpatialWeatherField.js";


import { DebugPanel } from "./ui/DebugPanel.js";
import { CameraDebugPanel } from "./ui/CameraDebugPanel.js";
import { TimePanel } from "./ui/TimePanel.js";
import { ERA5Panel } from "./ui/ERA5Panel.js";

import {
    LocalWeatherDataSource
} from "./weather/LocalWeatherDataSource.js";

import {
    WeatherStatistics
} from "./weather/WeatherStatistics.js";

import {
    WeatherBaseline
} from "./weather/WeatherBaseline.js";

import {
    AnomalyCalculator
} from "./weather/AnomalyCalculator.js";

import {
    PrototypeWeatherGenerator
} from "./weather/PrototypeWeatherGenerator.js";

import {
    VisualizationLoader
} from "./visualization/VisualizationLoader.js";

import {
    VariableGraph
} from "./visualization/graphs/VariableGraph.js";

import { TimeController } from "./time/TimeController.js";
import { TimeSliderPanel } from "./ui/TimeSliderPanel.js";

import { WeatherAPI } from "./api/WeatherAPI.js";

import { VisibleRegion } from "./lod/VisibleRegion.js";
import { DataLODController } from "./lod/DataLODController.js";

import { GeographicMap } from "./ui/GeographicMap.js";

import { GeographicSelectionPanel } from "./ui/GeographicSelectionPanel.js";
import { WeatherGraphPanel } from "./ui/WeatherGraphPanel.js";
import {
    ScientificAnalysisPanel
} from "./ui/ScientificAnalysisPanel.js";

// --------------------------------------------------
// Core
// --------------------------------------------------

const earth =
    new Earth();

const icosahedron =
    new Icosahedron(
        earth.radius
    );

const time =
    new Time();


// --------------------------------------------------
// Icosahedron Subdivision
// --------------------------------------------------

icosahedron.subdivide();

console.log(
    "Cell 20 Center:",
    icosahedron.cells[0].center
);

const cellCenter =
    icosahedron.cells[0].center;

const cellCoordinate =
    cartesianToGeo(
        cellCenter,
        earth.radius
    );

console.log(
    "Cell 20 Geographic Center:",
    cellCoordinate
);

console.log(
    "Icosahedron Level:",
    icosahedron.getLevel()
);

console.log(
    "Vertices:",
    icosahedron.getVertexCount()
);

console.log(
    "Edges:",
    icosahedron.getEdgeCount()
);

console.log(
    "Faces:",
    icosahedron.getFaceCount()
);

console.log(
    "Cells:",
    icosahedron.getCellCount()
);

console.log(
    "First Level 1 Cell:",
    icosahedron.cells[0]
);

console.log(
    "Its Parent:",
    icosahedron.cells[0].parent
);

console.log(
    "Parent Children:",
    icosahedron.cells[0].parent.children
);


// --------------------------------------------------
// Scene
// --------------------------------------------------

const scene =
    new THREE.Scene();


// --------------------------------------------------
// Camera
// --------------------------------------------------

const camera =
    new Camera();



// --------------------------------------------------
// Globe Viewport
// --------------------------------------------------

const globeViewport = document.createElement("section");

Object.assign(globeViewport.style, {
    position: "relative",
    width: "100%",
    height: "72vh",
    minHeight: "480px",
    boxSizing: "border-box",
    overflow: "hidden",
    flex: "none",
    background: "#05070d"
});

// Let the document grow and scroll vertically.
Object.assign(document.body.style, {
    margin: "0",
    minHeight: "100vh",
    overflowX: "hidden",
    overflowY: "auto"
});

document.body.appendChild(globeViewport);
// --------------------------------------------------
// Renderer
// --------------------------------------------------

const renderer = new Renderer(globeViewport);

// --------------------------------------------------
// Input
// --------------------------------------------------

const input =
    new Input(
        renderer.renderer.domElement
    );


// --------------------------------------------------
// Orbit Controller
// --------------------------------------------------

const orbitController =
    new OrbitController(
        camera,
        input
    );


// --------------------------------------------------
// Data LOD
// --------------------------------------------------

const initialCameraDistance = orbitController.distance;

const visibleRegionCalculator =
    new VisibleRegion({
        sphereRadius: earth.radius,
        samplesX: 32,
        samplesY: 32,
        paddingDegrees: 1.0
    });

const dataLODController =
    new DataLODController({
        initialDistance: initialCameraDistance
    });

let lodUpdateAccumulator = 0;
let previousLODState = null;

console.log("[Data LOD] Baseline established:", {
    initialCameraDistance,
    initialLevel: 0
});


// --------------------------------------------------
// Debug Panels
// --------------------------------------------------

const gisDebugPanel =
    new DebugPanel(globeViewport);

const cameraDebugPanel =
    new CameraDebugPanel(globeViewport);

const timePanel =
    new TimePanel();



// --------------------------------------------------
// Camera Navigation
// --------------------------------------------------

cameraDebugPanel.goToButton
    .addEventListener(
        "click",
        () => {
            const coordinate =
                cameraDebugPanel
                    .getTargetCoordinate();

            const position =
                geoToCartesian(
                    coordinate,
                    earth.radius
                );

            orbitController.goToLocation(
                position
            );
        }
    );


// --------------------------------------------------
// Earth
// --------------------------------------------------

const earthGeometry =
    new THREE.SphereGeometry(
        earth.radius,
        64,
        32
    );

const earthMaterial =
    new THREE.MeshBasicMaterial({
        wireframe: true
    });

const globe =
    new THREE.Mesh(
        earthGeometry,
        earthMaterial
    );

scene.add(
    globe
);

// --------------------------------------------------
// Icosahedron Visualization
// --------------------------------------------------

const icosahedronVisualizer =
    new IcosahedronVisualizer(
        scene,
        icosahedron
    );

// --------------------------------------------------
// Weather Visualization
// --------------------------------------------------

const weatherVisualizer =
    new WeatherVisualizer(
        scene,
        earth
    );



// --------------------------------------------------
// ERA5 Historical Weather
// --------------------------------------------------


const weatherAPI = new WeatherAPI();

let activeWeatherVariable = "temperature";
let activeWeatherTime = "2019-07-15T12:00:00";

let lastRequestedPlanKey = null;
let activeFrameRequestId = 0;
let lastFrameRequestTime = 0;
let nextFrameRetryTime = 0;
let frameRequestInFlight = false;

const FRAME_REQUEST_INTERVAL_MS = 500;
const FRAME_RETRY_DELAY_MS = 5000;
let era5Panel = null;


async function requestLODWeatherFrame(lodState) {
    const region = lodState?.visibleRegion;

    if (!region?.visible || !activeWeatherTime) {
        return;
    }

    // The backend does not yet support antimeridian-crossing bounds.
    if (region.crossesAntimeridian) {
        console.debug(
            "[Data LOD] Skipping frame request: region crosses antimeridian."
        );
        return;
    }

    const plan = dataLODController.createRequestPlan(lodState, {
        variable: activeWeatherVariable,
        time: activeWeatherTime
    });

    if (!plan) {
        return;
    }

    // Display the requested grid dimensions before fetching.
    era5Panel?.setGridInfo({
        maxRows: plan.maxRows,
        maxColumns: plan.maxColumns,
        pointBudget: plan.pointBudget,
        lodLevel: plan.geometricLevel
    });

    const planKey = [
        plan.variable,
        plan.time,
        plan.geometricLevel,
        plan.dataLevel,
        plan.maxRows,
        plan.maxColumns,
        dataLODController.getRegionKey(region)
    ].join("|");

    if (performance.now() < nextFrameRetryTime) {
        return;
    }

    if (planKey === lastRequestedPlanKey) {
        return;
    }

    // Never start a second ERA5 request while one is running.
    if (frameRequestInFlight) {
        return;
    }

    const now = performance.now();

    if (now - lastFrameRequestTime < FRAME_REQUEST_INTERVAL_MS) {
        return;
    }

    lastFrameRequestTime = now;
    lastRequestedPlanKey = planKey;

    const requestId = ++activeFrameRequestId;
    frameRequestInFlight = true;

    try {
        console.log("[Data LOD] Requesting ERA5 frame:", plan);

        const frame = await weatherAPI.getWeatherFrame({
            variable: plan.variable,
            time: plan.time,
            minLatitude: plan.minLatitude,
            maxLatitude: plan.maxLatitude,
            minLongitude: plan.minLongitude,
            maxLongitude: plan.maxLongitude,
            maxRows: plan.maxRows,
            maxColumns: plan.maxColumns
        });

        // Ignore a stale response.
        if (requestId !== activeFrameRequestId) {
            return;
        }

        // Display the actual dimensions returned by the backend.
        era5Panel?.setGridInfo({
            maxRows: plan.maxRows,
            maxColumns: plan.maxColumns,
            pointBudget: plan.pointBudget,
            lodLevel: plan.geometricLevel,
            actualRows: frame.height,
            actualColumns: frame.width
        });

        console.log("[Data LOD] ERA5 frame received:", {
            variable: frame.variable,
            time: frame.time,
            width: frame.width,
            height: frame.height,
            region: frame.region,
            sampling: frame.sampling
        });

        weatherVisualizer.displayERA5Frame(frame);
    } catch (error) {
        if (requestId === activeFrameRequestId) {
            lastRequestedPlanKey = null;
            nextFrameRetryTime =
                performance.now() + FRAME_RETRY_DELAY_MS;
        }

        console.error(
            "[Data LOD] ERA5 request failed; retry delayed:",
            error
        );
    } finally {
        frameRequestInFlight = false;
    }
}


async function initializeERA5() {
    try {
        era5Panel = new ERA5Panel(
            globeViewport,
            async ({
                variable,
                time,
                level,
                pointBudget,
                maxRows,
                maxColumns
            }) => {
                console.log("[ERA5] Requesting weather frame:", {
                    variable,
                    time,
                    level,
                    pointBudget,
                    requestedRows: maxRows,
                    requestedColumns: maxColumns,
                    requestedPoints: maxRows * maxColumns
                });

                const frame = await weatherAPI.getWeatherFrame({
                    variable,
                    time,
                    minLatitude: -90,
                    maxLatitude: 90,
                    minLongitude: -180,
                    maxLongitude: 180,
                    maxRows,
                    maxColumns
                });

                console.log("[ERA5] Weather frame received:", {
                    variable: frame.variable,
                    time: frame.time,
                    unit: frame.unit,
                    requestedLevel: level,
                    pointBudget,
                    width: frame.width,
                    height: frame.height,
                    actualPoints: frame.width * frame.height,
                    sampling: frame.sampling
                });

                weatherVisualizer.displayERA5Frame(frame);

                // The panel uses this to display the actual grid dimensions.
                return frame;
            }
        );

        console.log("[ERA5] Weather panel initialized.");
    } catch (error) {
        console.error("[ERA5] Initialization failed:", error);
    }
}

initializeERA5();



// --------------------------------------------------
// Weather
// --------------------------------------------------

const weatherDataSource =
    new LocalWeatherDataSource(
        "/data/weather/prototype_weather.json"
    );

const weatherField =
    new WeatherField();

let weatherObservations = [];

weatherDataSource
    .load()
    .then(
        observations => {
            weatherObservations =
                observations;

            weatherField.addObservations(
                observations
            );

            console.log(
                "Loaded weather observations:",
                weatherObservations
            );

            console.log(
                "Weather field:",
                weatherField
            );

            weatherVisualizer.displayObservations(
                weatherObservations,
                icosahedron
            );

            for (const observation of weatherObservations) {
                console.log(
                    "Weather Observation:",
                    observation
                );

                console.log(
                    "Associated Cell:",
                    observation.cell
                );
            }

            // --------------------------------------------------
            // Weather Field Tests
            // --------------------------------------------------

            console.log(
                "Valid Times:",
                [...weatherField.getValidTimes()]
            );

            console.log(
                "Ensemble Members:",
                [
                    ...weatherField.getEnsembleMembers(
                        "2026-09-27T06:00:00Z"
                    )
                ]
            );

            console.log(
                "12:00 Ensemble 1:",
                weatherField.getObservationsAt(
                    "2026-09-27T12:00:00Z",
                    1
                )
            );

            console.log(
                "18:00 Ensemble 0:",
                weatherField.getObservationsAt(
                    "2026-09-27T18:00:00Z",
                    0
                )
            );

            console.log(
                "Observations:",
                weatherField.getObservationsAt(
                    "2026-09-27T06:00:00Z",
                    0
                )
            );
            const spatialField =
                weatherField.getField(
                    "2026-09-27T12:00:00Z",
                    1
                );

            console.log(
                "Spatial Weather Field:",
                spatialField
            );

            const spatialWeatherField =
                new SpatialWeatherField(
                    earth
                );

            spatialWeatherField.addObservations(
                spatialField,
                icosahedron
            );

            const temperatureStatistics =
                WeatherStatistics.calculate(
                    spatialWeatherField.getObservations(),
                    "temperature"
                );

            console.log(
                "Temperature Statistics:",
                temperatureStatistics
            );
            const cell20Observations =
                spatialWeatherField.getCellObservations(
                    20
                );

            const cell20TemperatureStatistics =
                WeatherStatistics.calculate(
                    cell20Observations,
                    "temperature"
                );

            console.log(
                "Cell 20 Temperature Statistics:",
                cell20TemperatureStatistics
            );

            console.log(
                "Spatial Weather Representation:",
                spatialWeatherField
            );
            console.log(
                "Spatial Cell IDs:",
                [
                    ...spatialWeatherField.getCellIds()
                ]
            );
            console.log(
                "Observations in Cell 20:",
                spatialWeatherField.getCellObservations(
                    20
                )
            );

            console.log(
                "Spatial Weather Field"
            );

            console.log(
                "Observation Count:",
                spatialWeatherField.getObservationCount()
            );

            console.log(
                "Cell Count:",
                spatialWeatherField.getCellCount()
            );

            for (const cellId of spatialWeatherField.getCellIds()) {
                console.log(
                    "Cell:",
                    cellId,
                    "Observations:",
                    spatialWeatherField.getCellObservations(
                        cellId
                    )
                );
            }

            const weatherBaseline =
                new WeatherBaseline();

            weatherBaseline.set(
                "78.9629,20.5937",
                "temperature",
                28.0
            );

            weatherBaseline.set(
                "79.9629,20.5937",
                "temperature",
                27.5
            );

            weatherBaseline.set(
                "78.9629,21.5937",
                "temperature",
                27.0
            );
            console.log(
                "Baseline Temperature:",
                weatherBaseline.get(
                    "78.9629,20.5937",
                    "temperature"
                )
            );
            console.log(
                "Baseline 1:",
                weatherBaseline.get(
                    "78.9629,20.5937",
                    "temperature"
                )
            );

            console.log(
                "Baseline 2:",
                weatherBaseline.get(
                    "79.9629,20.5937",
                    "temperature"
                )
            );

            console.log(
                "Baseline 3:",
                weatherBaseline.get(
                    "78.9629,21.5937",
                    "temperature"
                )
            );
            const testObservation =
                spatialWeatherField.getObservations()[0];

            const testBaseline =
                weatherBaseline.get(
                    `${testObservation.longitude},${testObservation.latitude}`,
                    "temperature"
                );

            const temperatureAnomaly =
                AnomalyCalculator.calculate(
                    testObservation,
                    testBaseline,
                    "temperature"
                );

            console.log(
                "Temperature Anomaly:",
                temperatureAnomaly
            );
            const prototypeGenerator =
                new PrototypeWeatherGenerator({
                    longitudeStep: 5,
                    latitudeStep: 5,

                    validTimes: [
                        "2026-09-27T06:00:00Z",
                        "2026-09-27T12:00:00Z",
                        "2026-09-27T18:00:00Z"
                    ],

                    ensembleMembers: [
                        0,
                        1
                    ]
                });

            const globalObservations =
                prototypeGenerator.generate();

            console.log(
                "Global Prototype Observations:",
                globalObservations
            );

            console.log(
                "Global Observation Count:",
                globalObservations.length
            );
            const anomalyCenterObservation =
                globalObservations.find(
                    observation =>
                        observation.validTime ===
                        "2026-09-27T06:00:00Z" &&
                        observation.longitude === 60 &&
                        observation.latitude === 20
                );

            console.log(
                "Initial Anomaly Center:",
                anomalyCenterObservation
            );
            const movingAnomalyObservations =
                globalObservations.filter(
                    observation =>
                        observation.latitude === 20 &&
                        (
                            observation.longitude === 60 ||
                            observation.longitude === 70 ||
                            observation.longitude === 80
                        )
                );

            console.log(
                "Moving Anomaly Samples:",
                movingAnomalyObservations
            );
        }
    )
    .catch(
        error => {
            console.error(
                "Failed to load weather data:",
                error
            );
        }
    );

/*
 * --------------------------------------------------
 * Python Visualization Data
 * --------------------------------------------------
 */

const visualizationLoader = new VisualizationLoader();

let visualizationData = null;
let activeVariableGraph = null;


/*
 * --------------------------------------------------
 * Universal Time Controller
 * --------------------------------------------------
 */

const timeController = new TimeController({
    frameInterval: 750,
    playbackSpeed: 1.0
});

console.log(
    "[Temporal Model] Reference:",
    timeController.getReferenceTime().toISOString()
);

timeController.setTimeOffset(-24 * 60 * 60);

console.log(
    "[Temporal Model] 24 hours before:",
    timeController.getSelectedTime().toISOString()
);

console.log(
    "[Temporal Model] Offset in seconds:",
    timeController.getTimeOffset()
);

const timeSliderPanel = new TimeSliderPanel(timeController);

console.log("Time Slider Panel initialized.");


/*
 * --------------------------------------------------
 * Geographic Map and Weather Graph
 * --------------------------------------------------
 */

const geographicMap = new GeographicMap();

const weatherGraphPanel = new WeatherGraphPanel(
    document.body,
    {
        variables: [
            { id: "temperature", label: "Temperature", unit: "°C" },
            { id: "dewpoint", label: "Dewpoint", unit: "°C" },
            {
                id: "mean_sea_level_pressure",
                label: "Mean Sea Level Pressure",
                unit: "hPa"
            },
            {
                id: "surface_pressure",
                label: "Surface Pressure",
                unit: "hPa"
            },
            { id: "wind_u", label: "U Wind Component", unit: "m/s" },
            { id: "wind_v", label: "V Wind Component", unit: "m/s" },
            { id: "precipitation", label: "Total Precipitation", unit: "mm" }
        ]
    }
);


/*
 * --------------------------------------------------
 * Historical ERA5 Metadata
 * --------------------------------------------------
 */

let historicalMetadata = null;
let historicalRequestId = 0;

async function loadHistoricalMetadata() {
    try {
        historicalMetadata = await weatherAPI.getMetadata();

        console.log(
            "[ERA5 History] Dataset metadata:",
            historicalMetadata
        );
    } catch (error) {
        console.error(
            "[ERA5 History] Metadata request failed:",
            error
        );
    }
}

loadHistoricalMetadata();


/*
 * --------------------------------------------------
 * Scientific Analysis Panel
 * --------------------------------------------------
 *
 * Declare this BEFORE the geographic selection callback,
 * because that callback references this panel.
 */

const scientificAnalysisPanel = new ScientificAnalysisPanel(
    document.body,

    async configuration => {
        const result = await weatherAPI.runScientificAnalysis(
            configuration
        );

        if (!Array.isArray(result.frames)) {
            throw new Error(
                "The analysis response does not contain a frames array."
            );
        }

        if (result.frames.length === 0) {
            throw new Error(
                "The analysis returned no visualization frames."
            );
        }

        visualizationData = result;

        console.log("[Scientific Analysis] Result received:", {
            variable: result.variable,
            frameCount: result.frame_count ?? result.frames.length,
            trackCount: result.tracks?.length ?? 0,
            eventCount: result.events?.length ?? 0
        });

        // Switch the shared timeline to the scientific result.
        timeController.setFrames(result.frames);

        // Refresh the graph to the selected analysis frame.
        const frame = timeController.getCurrentFrame();

        if (activeVariableGraph && frame) {
            activeVariableGraph.setFrame(frame);
        }

        return result;
    }
);


/*
 * --------------------------------------------------
 * Geographic Selection Panel
 * --------------------------------------------------
 */

const geographicSelectionPanel = new GeographicSelectionPanel(
    document.body,

    selection => {
        console.log("[Geographic Selection]", selection);

        weatherGraphPanel.setSelection?.(selection);

        // Share the selected point/region with scientific analysis.
        scientificAnalysisPanel.setSelection(selection);
    },

    geographicMap,

    async selection => {
        if (!selection) {
            return;
        }

        const requestId = ++historicalRequestId;

        /*
         * --------------------------------------------------
         * Regional Statistics
         * --------------------------------------------------
         */

        if (selection.type === "region") {
            try {
                geographicSelectionPanel.fetchButton.disabled = true;
                weatherGraphPanel.setLoading(true);

                geographicSelectionPanel.setStatus(
                    "Calculating regional ERA5 statistics..."
                );

                if (!historicalMetadata) {
                    historicalMetadata = await weatherAPI.getMetadata();
                }

                const currentTime = timeController.getCurrentTime();

                if (!currentTime) {
                    throw new Error(
                        "Could not determine the current timeline timestamp."
                    );
                }

                const time = currentTime instanceof Date
                    ? currentTime.toISOString().replace(/\.000Z$/, "")
                    : String(currentTime);

                const { bounds } = selection;

                const variables = [
                    "temperature",
                    "dewpoint",
                    "mean_sea_level_pressure",
                    "surface_pressure",
                    "wind_u",
                    "wind_v",
                    "total_precipitation"
                ];

                const results = await Promise.all(
                    variables.map(variable =>
                        weatherAPI.getRegionStatistics({
                            variable,
                            time,
                            minLatitude: bounds.minLatitude,
                            maxLatitude: bounds.maxLatitude,
                            minLongitude: bounds.minLongitude,
                            maxLongitude: bounds.maxLongitude
                        })
                    )
                );

                if (requestId !== historicalRequestId) {
                    return;
                }

                console.log("[ERA5 Regional Statistics]", {
                    time,
                    bounds,
                    results
                });

                geographicSelectionPanel.setStatus(
                    `Regional statistics loaded for ${results.length} variables ` +
                    `at ${time}. Check the console for results.`
                );

                geographicSelectionPanel.setRegionalStatistics?.({
                    time,
                    bounds,
                    results
                });
            } catch (error) {
                if (requestId === historicalRequestId) {
                    weatherGraphPanel.setError(error.message);

                    geographicSelectionPanel.setStatus(
                        `Regional statistics request failed: ${error.message}`
                    );
                }

                console.error(
                    "[ERA5 Regional Statistics] Request failed:",
                    error
                );
            } finally {
                if (requestId === historicalRequestId) {
                    geographicSelectionPanel.fetchButton.disabled = false;
                    weatherGraphPanel.setLoading(false);
                }
            }

            return;
        }

        /*
         * --------------------------------------------------
         * Point Historical Time Series
         * --------------------------------------------------
         */

        try {
            geographicSelectionPanel.fetchButton.disabled = true;

            geographicSelectionPanel.setStatus(
                "Fetching historical ERA5 data..."
            );

            weatherGraphPanel.setLoading(true);

            if (!historicalMetadata) {
                historicalMetadata = await weatherAPI.getMetadata();
            }

            const startTime = historicalMetadata.time.first;
            const endTime = historicalMetadata.time.last;

            const variables = [
                "temperature",
                "dewpoint",
                "mean_sea_level_pressure",
                "surface_pressure",
                "wind_u",
                "wind_v",
                "total_precipitation"
            ];

            const results = await Promise.all(
                variables.map(variable =>
                    weatherAPI.getTimeSeries({
                        variable,
                        startTime,
                        endTime,
                        latitude: selection.latitude,
                        longitude: selection.longitude,
                        timeStep: 1
                    })
                )
            );

            if (requestId !== historicalRequestId) {
                return;
            }

            const timestamps = results[0].timestamps;

            const series = results.map(result => ({
                id: result.variable === "total_precipitation"
                    ? "precipitation"
                    : result.variable,
                values: result.values
            }));

            weatherGraphPanel.setData({
                timestamps,
                series
            });

            const firstResult = results[0];

            geographicSelectionPanel.setStatus(
                `Loaded ${timestamps.length} timestamps for ` +
                `ERA5 grid point ${firstResult.latitude.toFixed(3)}°, ` +
                `${firstResult.longitude.toFixed(3)}°. ` +
                `Period: ${startTime} to ${endTime}.`
            );

            console.log("[ERA5 History] Time series loaded:", {
                requestedCoordinate: {
                    latitude: selection.latitude,
                    longitude: selection.longitude
                },
                actualGridCoordinate: {
                    latitude: firstResult.latitude,
                    longitude: firstResult.longitude
                },
                timestamps: timestamps.length,
                series
            });
        } catch (error) {
            if (requestId === historicalRequestId) {
                weatherGraphPanel.setError(error.message);

                geographicSelectionPanel.setStatus(
                    `Historical data request failed: ${error.message}`
                );
            }

            console.error(
                "[ERA5 History] Request failed:",
                error
            );
        } finally {
            if (requestId === historicalRequestId) {
                geographicSelectionPanel.fetchButton.disabled = false;
                weatherGraphPanel.setLoading(false);
            }
        }
    }
);


/*
 * --------------------------------------------------
 * Panel Layout
 * --------------------------------------------------
 */

timeSliderPanel.panel.insertAdjacentElement(
    "afterend",
    geographicSelectionPanel.element
);

geographicSelectionPanel.element.insertAdjacentElement(
    "afterend",
    scientificAnalysisPanel.element
);

// The map's interactive selection behavior remains available
// through GeographicSelectionPanel. Remove its standalone element.
geographicMap.element.remove();

console.log("[Avani] Historical and scientific panels initialized.");


/*
 * --------------------------------------------------
 * Load Default Visualization Timeline
 * --------------------------------------------------
 */

visualizationLoader
    .load("/data/visualization/timeline.json")
    .then(data => {
        visualizationData = data;

        console.log(
            "[Visualization] Loaded data:",
            visualizationData
        );

        console.log(
            "[Visualization] Summary:",
            visualizationData.getSummary()
        );

        for (
            let i = 0;
            i < visualizationData.getFrameCount();
            i++
        ) {
            const frame = visualizationData.getFrame(i);

            console.log(
                "[Visualization] Frame:",
                i,
                frame.time,
                "Anomalies:",
                frame.anomalies?.length ?? 0,
                "Regions:",
                frame.regions?.length ?? 0
            );
        }

        /*
         * --------------------------------------------------
         * Initialize Timeline
         * --------------------------------------------------
         */

        timeController.setFrames(visualizationData.frames);

        console.log("[Time Controller] Initialized:", {
            frameCount: timeController.getFrameCount(),
            currentIndex: timeController.getCurrentIndex(),
            currentTime: timeController.getCurrentTime()
        });

        /*
         * --------------------------------------------------
         * Variable Graph
         * --------------------------------------------------
         */

        const variableGraph = new VariableGraph({
            radius: 1.002,
            pointSize: 0.025,
            wrapLongitude: true
        });

        activeVariableGraph = variableGraph;

        scene.add(variableGraph.getObject());

        /*
         * --------------------------------------------------
         * Timeline → Variable Graph
         * --------------------------------------------------
         *
         * Only one listener is needed. It handles both the
         * default timeline and subsequent scientific analyses.
         */

        timeController.addListener(state => {
            if (!state.frame) {
                return;
            }

            variableGraph.setFrame(state.frame);

            console.log("[Time Controller] Frame updated:", {
                index: state.index,
                frameCount: state.frameCount,
                time: state.time,
                playing: state.playing,
                samples: variableGraph.getSampleCount(),
                minimum: variableGraph.getMinimumValue(),
                maximum: variableGraph.getMaximumValue()
            });
        });

        // Explicitly initialize the graph for the current frame.
        const firstFrame = timeController.getCurrentFrame();

        if (firstFrame) {
            variableGraph.setFrame(firstFrame);
        }

        console.log("[Variable Graph] Created:", {
            samples: variableGraph.getSampleCount(),
            rows: variableGraph.getGridRows(),
            columns: variableGraph.getGridColumns(),
            cells: variableGraph.getCellCount(),
            minimum: variableGraph.getMinimumValue(),
            maximum: variableGraph.getMaximumValue()
        });

        console.log(
            "[Avani] Universal visualization timeline ready."
        );
    })
    .catch(error => {
        console.error(
            "[Visualization] Failed to load default timeline:",
            error
        );
    });

// --------------------------------------------------
// GIS Debug Point
// --------------------------------------------------

const pointGeometry =
    new THREE.SphereGeometry(
        0.025,
        16,
        16
    );

const pointMaterial =
    new THREE.MeshBasicMaterial({
        color: 0xff3333
    });

const debugPoint =
    new THREE.Mesh(
        pointGeometry,
        pointMaterial
    );

scene.add(
    debugPoint
);


// --------------------------------------------------
// GIS Point Update
// --------------------------------------------------

function updateGISPoint() {
    const coordinate =
        gisDebugPanel.getCoordinate();

    const position =
        geoToCartesian(
            coordinate,
            earth.radius
        );

    debugPoint.position.copy(
        position
    );

    gisDebugPanel.update(
        coordinate,
        position
    );


    const cell =
        icosahedron.findCell(
            position
        );

    console.log(
        "Current GIS Cell:",
        cell
    );


    // Highlight the cell containing
    // the current GIS position.

    icosahedronVisualizer.highlightCell(
        cell
    );
}

gisDebugPanel.longitudeInput
    .addEventListener(
        "input",
        updateGISPoint
    );

gisDebugPanel.latitudeInput
    .addEventListener(
        "input",
        updateGISPoint
    );

gisDebugPanel.heightInput
    .addEventListener(
        "input",
        updateGISPoint
    );

updateGISPoint();

const testCoordinate =
    gisDebugPanel.getCoordinate();

const testPosition =
    geoToCartesian(
        testCoordinate,
        earth.radius
    );

const foundCell =
    icosahedron.findCell(
        testPosition
    );

console.log(
    "GIS Test Coordinate:",
    testCoordinate
);

console.log(
    "Found Cell:",
    foundCell
);


// --------------------------------------------------
// Camera → Earth Center Line
// --------------------------------------------------

const cameraLineGeometry =
    new THREE.BufferGeometry();

const cameraLineMaterial =
    new THREE.LineBasicMaterial({
        color: 0x00ff00
    });

const cameraLine =
    new THREE.Line(
        cameraLineGeometry,
        cameraLineMaterial
    );

scene.add(
    cameraLine
);


// --------------------------------------------------
// Camera Look Point
// --------------------------------------------------

const cameraLookPointGeometry =
    new THREE.SphereGeometry(
        0.018,
        12,
        12
    );

const cameraLookPointMaterial =
    new THREE.MeshBasicMaterial({
        color: 0xffff00
    });

const cameraLookPoint =
    new THREE.Mesh(
        cameraLookPointGeometry,
        cameraLookPointMaterial
    );

scene.add(
    cameraLookPoint
);


// --------------------------------------------------
// Camera Debug Update
// --------------------------------------------------

function updateCameraDebug() {
    const cameraPosition =
        camera.camera.position;

    const direction =
        new THREE.Vector3();

    camera.camera.getWorldDirection(
        direction
    );

    const intersection =
        raySphereIntersection(
            cameraPosition,
            direction,
            earth.radius
        );

    if (
        intersection !== null
    ) {
        cameraLookPoint.position.copy(
            intersection
        );

        const coordinate =
            cartesianToGeo(
                intersection,
                earth.radius
            );

        cameraDebugPanel.update(
            camera,
            coordinate
        );
    }
    else {
        cameraDebugPanel.update(
            camera,
            null
        );
    }


    const linePoints = [

        cameraPosition.clone(),

        new THREE.Vector3(
            0.0,
            0.0,
            0.0
        )
    ];

    cameraLineGeometry.setFromPoints(
        linePoints
    );
}


// --------------------------------------------------
// Resize
// --------------------------------------------------


function resize() {
    const width = globeViewport.clientWidth;
    const height = globeViewport.clientHeight;

    camera.resize(width, height);
    renderer.resize(width, height);
}

window.addEventListener("resize", resize);
resize();

// --------------------------------------------------
// Main Loop
// --------------------------------------------------

function animate() {
    requestAnimationFrame(
        animate
    );


    // ----------------------------------------------
    // Time
    // ----------------------------------------------

    time.update();

    const deltaTime =
        time.getDeltaTime();

    timePanel.update(
        time
    );


    // ----------------------------------------------
    // Camera
    // ----------------------------------------------

    orbitController.update(
        deltaTime
    );


    // ----------------------------------------------
    // Data LOD: Visible Geographic Region
    // ----------------------------------------------

    lodUpdateAccumulator += deltaTime;

    // Update at 5 Hz instead of calculating 1,089 rays
    // every rendered frame.
    if (lodUpdateAccumulator >= 0.2) {
        lodUpdateAccumulator %= 0.2;

        const visibleRegion =
            visibleRegionCalculator.calculate(
                camera.camera
            );

        if (visibleRegion.visible) {
            const lodState =
                dataLODController.update(
                    orbitController.distance,
                    visibleRegion
                );
            // requestLODWeatherFrame(lodState);

            const region = lodState.visibleRegion;

            const regionKey = [
                lodState.geometricLevel,
                region.minLatitude.toFixed(2),
                region.maxLatitude.toFixed(2),
                region.minLongitude.toFixed(2),
                region.maxLongitude.toFixed(2)
            ].join(":");

            if (regionKey !== previousLODState) {
                console.log("[Data LOD]", {
                    geometricLevel: lodState.geometricLevel,
                    dataLevel: lodState.dataLevel,
                    cameraDistance: lodState.cameraDistance,
                    sampleBudget: {
                        rows: lodState.maxRows,
                        columns: lodState.maxColumns
                    },
                    geographicBounds: {
                        minLatitude: region.minLatitude,
                        maxLatitude: region.maxLatitude,
                        minLongitude: region.minLongitude,
                        maxLongitude: region.maxLongitude,
                        crossesAntimeridian:
                            region.crossesAntimeridian
                    }
                });

                previousLODState = regionKey;
            }
        }
    }


    // ----------------------------------------------
    // Camera Debug
    // ----------------------------------------------

    updateCameraDebug();


    // ----------------------------------------------
    // Render
    // ----------------------------------------------

    renderer.render(
        scene,
        camera
    );
}

animate();