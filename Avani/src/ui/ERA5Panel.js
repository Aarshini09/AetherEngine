
const ERA5_VARIABLES = [
    { id: "temperature", name: "Temperature", unit: "°C" },
    { id: "dewpoint", name: "Dewpoint", unit: "°C" },
    {
        id: "mean_sea_level_pressure",
        name: "Mean Sea Level Pressure",
        unit: "hPa"
    },
    { id: "surface_pressure", name: "Surface Pressure", unit: "hPa" },
    { id: "wind_u", name: "Wind U", unit: "m/s" },
    { id: "wind_v", name: "Wind V", unit: "m/s" },
    { id: "total_precipitation", name: "Total Precipitation", unit: "mm" }
];

const RESOLUTION_LEVELS = [
    { level: 1, pointBudget: 10_000, name: "Preview" },
    { level: 2, pointBudget: 25_000, name: "Low" },
    { level: 3, pointBudget: 50_000, name: "Basic" },
    { level: 4, pointBudget: 100_000, name: "Regional" },
    { level: 5, pointBudget: 200_000, name: "Detailed" },
    { level: 6, pointBudget: 350_000, name: "High detail" },
    { level: 7, pointBudget: 500_000, name: "Very high" },
    { level: 8, pointBudget: 650_000, name: "Advanced" },
    { level: 9, pointBudget: 800_000, name: "Near maximum" },
    { level: 10, pointBudget: 1_000_000, name: "Maximum" }
];

const MAX_SOURCE_ROWS = 721;
const MAX_SOURCE_COLUMNS = 1440;

const DEFAULT_TIME = "2019-07-15T12:00";
const FIRST_TIME = "2015-01-01T00:00";
const LAST_TIME = "2019-12-31T18:00";

function calculateGridDimensions(pointBudget) {
    // Keep an approximately 1:2 rows-to-columns ratio.
    let rows = Math.min(
        MAX_SOURCE_ROWS,
        Math.max(2, Math.floor(Math.sqrt(pointBudget / 2)))
    );

    let columns = Math.min(
        MAX_SOURCE_COLUMNS,
        Math.max(2, Math.floor(pointBudget / rows))
    );

    // Enforce the budget even if dimensions are adjusted later.
    while (rows * columns > pointBudget && columns > 2) {
        columns--;
    }

    return {
        rows,
        columns,
        estimatedPoints: rows * columns
    };
}

export class ERA5Panel {
    constructor(container, onLoadFrame) {
        this.container = container;
        this.onLoadFrame = onLoadFrame;
        this.selectedVariable = "temperature";
        this.selectedLevel = 3;
        this.loading = false;

        this.createUI();
        this.updateGridInfo();
    }

    createUI() {
        this.element = document.createElement("section");

        Object.assign(this.element.style, {
            position: "absolute",
            top: "12px",
            right: "12px",
            zIndex: "20",
            width: "310px",
            maxWidth: "calc(100% - 24px)",
            maxHeight: "calc(100% - 24px)",
            overflowY: "auto",
            padding: "14px",
            boxSizing: "border-box",
            background: "rgba(12, 18, 30, 0.94)",
            color: "#e8edf7",
            border: "1px solid #344157",
            borderRadius: "8px",
            font: "13px/1.5 system-ui, sans-serif",
            boxShadow: "0 4px 20px rgba(0,0,0,0.35)"
        });

        const title = document.createElement("div");
        title.textContent = "ERA5 Historical Weather";

        Object.assign(title.style, {
            fontSize: "15px",
            fontWeight: "700",
            marginBottom: "12px"
        });

        this.element.appendChild(title);

        // Weather variable.
        this.addLabel("Weather variable");

        this.variableSelect = document.createElement("select");

        for (const variable of ERA5_VARIABLES) {
            const option = document.createElement("option");
            option.value = variable.id;
            option.textContent = `${variable.name} (${variable.unit})`;
            this.variableSelect.appendChild(option);
        }

        this.variableSelect.value = this.selectedVariable;
        this.styleControl(this.variableSelect);

        this.variableSelect.addEventListener("change", () => {
            this.selectedVariable = this.variableSelect.value;
        });

        this.element.appendChild(this.variableSelect);

        // Valid time.
        this.addLabel("Valid time (UTC)");

        this.timeInput = document.createElement("input");
        this.timeInput.type = "datetime-local";
        this.timeInput.step = "21600";
        this.timeInput.min = FIRST_TIME;
        this.timeInput.max = LAST_TIME;
        this.timeInput.value = DEFAULT_TIME;
        this.styleControl(this.timeInput);

        this.element.appendChild(this.timeInput);

        // User-controlled data resolution.
        this.addLabel("Data resolution");

        this.resolutionSelect = document.createElement("select");

        for (const resolution of RESOLUTION_LEVELS) {
            const option = document.createElement("option");
            option.value = String(resolution.level);
            option.textContent =
                `Level ${resolution.level} — ${resolution.name} ` +
                `(${resolution.pointBudget.toLocaleString()} points)`;

            this.resolutionSelect.appendChild(option);
        }

        this.resolutionSelect.value = String(this.selectedLevel);
        this.styleControl(this.resolutionSelect);

        this.resolutionSelect.addEventListener("change", () => {
            this.selectedLevel = Number(this.resolutionSelect.value);
            this.updateGridInfo();
        });

        this.element.appendChild(this.resolutionSelect);

        // Requested and actual grid information.
        this.gridInfo = document.createElement("div");

        Object.assign(this.gridInfo.style, {
            marginTop: "10px",
            padding: "10px",
            background: "rgba(255,255,255,0.045)",
            border: "1px solid #344157",
            borderRadius: "6px",
            overflowWrap: "anywhere"
        });

        this.element.appendChild(this.gridInfo);

        // Explicit fetch button.
        this.loadButton = document.createElement("button");
        this.loadButton.type = "button";
        this.loadButton.textContent = "Load Weather Frame";

        Object.assign(this.loadButton.style, {
            width: "100%",
            marginTop: "12px",
            padding: "9px",
            border: "0",
            borderRadius: "5px",
            background: "#3679d8",
            color: "#ffffff",
            fontWeight: "600",
            cursor: "pointer"
        });

        this.loadButton.addEventListener("click", () => {
            this.loadFrame();
        });

        this.element.appendChild(this.loadButton);

        this.status = document.createElement("div");
        this.status.textContent = "Ready to request ERA5 data.";

        Object.assign(this.status.style, {
            marginTop: "9px",
            color: "#9eabc0",
            overflowWrap: "anywhere"
        });

        this.element.appendChild(this.status);
        this.container.appendChild(this.element);
    }

    addLabel(text) {
        const label = document.createElement("label");
        label.textContent = text;

        Object.assign(label.style, {
            display: "block",
            marginTop: "8px",
            marginBottom: "4px",
            color: "#cbd5e4"
        });

        this.element.appendChild(label);
    }

    styleControl(control) {
        Object.assign(control.style, {
            display: "block",
            width: "100%",
            minWidth: "0",
            boxSizing: "border-box",
            padding: "8px",
            background: "#182235",
            color: "#e8edf7",
            border: "1px solid #40506a",
            borderRadius: "5px",
            font: "inherit"
        });
    }

    getSelectedResolution() {
        return RESOLUTION_LEVELS.find(
            item => item.level === this.selectedLevel
        );
    }

    updateGridInfo(actualRows = null, actualColumns = null) {
        const resolution = this.getSelectedResolution();
        const grid = calculateGridDimensions(resolution.pointBudget);

        this.requestedGrid = grid;

        this.gridInfo.replaceChildren();

        this.addInfoLine(
            "Resolution level",
            `${resolution.level} / 10`
        );

        this.addInfoLine(
            "Requested grid",
            `${grid.rows} rows × ${grid.columns} columns`
        );

        this.addInfoLine(
            "Requested points",
            `${grid.estimatedPoints.toLocaleString()} / ` +
            `${resolution.pointBudget.toLocaleString()}`
        );

        if (actualRows !== null && actualColumns !== null) {
            this.addInfoLine(
                "Actual grid",
                `${actualRows} rows × ${actualColumns} columns`
            );

            this.addInfoLine(
                "Actual points",
                (actualRows * actualColumns).toLocaleString()
            );
        }
    }

    addInfoLine(label, value) {
        const line = document.createElement("div");

        Object.assign(line.style, {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "8px",
            marginBottom: "3px"
        });

        const labelElement = document.createElement("span");
        labelElement.textContent = label;
        labelElement.style.color = "#9eabc0";

        const valueElement = document.createElement("span");
        valueElement.textContent = value;
        valueElement.style.textAlign = "right";
        valueElement.style.fontWeight = "600";

        line.append(labelElement, valueElement);
        this.gridInfo.appendChild(line);
    }

    async loadFrame() {
        if (this.loading) return;

        if (!this.timeInput.value) {
            this.status.textContent = "Choose a timestamp first.";
            return;
        }

        this.loading = true;
        this.loadButton.disabled = true;
        this.loadButton.textContent = "Loading...";
        this.status.textContent = "Requesting ERA5 weather data...";

        const resolution = this.getSelectedResolution();
        const grid = calculateGridDimensions(resolution.pointBudget);

        this.updateGridInfo();

        try {
            const time =
                `${this.timeInput.value.replace("T", " ")}:00`;

            const frame = await this.onLoadFrame({
                variable: this.selectedVariable,
                time,
                level: resolution.level,
                pointBudget: resolution.pointBudget,
                maxRows: grid.rows,
                maxColumns: grid.columns
            });

            if (frame) {
                this.updateGridInfo(frame.height, frame.width);

                this.status.textContent =
                    `Loaded ${frame.variable} · ${frame.time} UTC`;
            } else {
                this.status.textContent =
                    "Request completed, but no frame was returned.";
            }
        } catch (error) {
            console.error("[ERA5 Panel]", error);
            this.status.textContent = `Error: ${error.message}`;
        } finally {
            this.loading = false;
            this.loadButton.disabled = false;
            this.loadButton.textContent = "Load Weather Frame";
        }
    }
}
