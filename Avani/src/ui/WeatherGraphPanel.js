
const GRAPH_COLORS = {
    temperature: "#55c8ff",
    dewpoint: "#8b9cff",
    mean_sea_level_pressure: "#f2bd5b",
    surface_pressure: "#ff8b67",
    humidity: "#5de0b0",
    wind_speed: "#ed86d4",
    wind_u: "#b69cff",
    wind_v: "#ff9a9a",
    precipitation: "#64a8ff"
};

const DEFAULT_VARIABLES = [
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
    { id: "humidity", label: "Humidity", unit: "%" },
    { id: "wind_speed", label: "Wind Speed", unit: "m/s" },
    { id: "wind_u", label: "U Wind Component", unit: "m/s" },
    { id: "wind_v", label: "V Wind Component", unit: "m/s" },
    { id: "precipitation", label: "Precipitation", unit: "mm" }
];

export class WeatherGraphPanel {
    constructor(container, options = {}) {
        this.container = container;
        this.variables = options.variables ?? DEFAULT_VARIABLES;
        this.timestamps = [];
        this.series = [];
        this.enabledVariables = new Set(
            this.variables.map(variable => variable.id)
        );

        this.element = document.createElement("section");

        Object.assign(this.element.style, {
            width: "calc(100% - 32px)",
            maxWidth: "1568px",
            boxSizing: "border-box",
            margin: "24px auto",
            padding: "20px",
            background: "#0b111c",
            color: "#e8edf7",
            border: "1px solid #344157",
            borderRadius: "10px",
            font: "13px/1.5 system-ui, sans-serif"
        });

        this.injectStyles();
        this.createUI();

        this.container.appendChild(this.element);
        this.render();
    }

    injectStyles() {
        if (document.getElementById("avani-weather-graph-styles")) {
            return;
        }

        const style = document.createElement("style");
        style.id = "avani-weather-graph-styles";

        style.textContent = `
            .av-graph-grid {
                display: grid;
                grid-template-columns: repeat(
                    auto-fit, minmax(min(100%, 320px), 1fr)
                );
                gap: 14px;
            }

            .av-graph-card {
                min-width: 0;
                padding: 14px;
                background: #101927;
                border: 1px solid #293951;
                border-radius: 8px;
            }

            .av-graph-heading {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 12px;
            }

            .av-graph-title {
                font-weight: 700;
                font-size: 14px;
                color: #e8edf7;
            }

            .av-graph-subtitle {
                margin-top: 3px;
                font-size: 11px;
                color: #8fa2bc;
            }

            .av-graph-svg {
                display: block;
                width: 100%;
                height: auto;
                overflow: visible;
            }

            .av-graph-legend {
                display: flex;
                flex-wrap: wrap;
                gap: 7px;
                margin-top: 10px;
            }

            .av-graph-toggle {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 8px;
                background: #172337;
                border: 1px solid #344157;
                border-radius: 5px;
                color: #cbd5e4;
                font: inherit;
                font-size: 11px;
                cursor: pointer;
            }

            .av-graph-toggle[aria-pressed="false"] {
                opacity: 0.45;
            }

            .av-graph-toggle:focus-visible {
                outline: 2px solid #55c8ff;
                outline-offset: 2px;
            }

            .av-graph-empty {
                display: grid;
                place-items: center;
                min-height: 155px;
                padding: 18px;
                box-sizing: border-box;
                border: 1px dashed #344157;
                border-radius: 6px;
                text-align: center;
                color: #8fa2bc;
                font-size: 12px;
            }

            .av-graph-tooltip {
                padding: 9px 11px;
                background: #172337;
                border: 1px solid #405574;
                border-radius: 6px;
                color: #e8edf7;
                font-size: 11px;
                overflow-wrap: anywhere;
            }

            .av-graph-stat {
                display: flex;
                justify-content: space-between;
                gap: 12px;
                padding: 7px 0;
                border-bottom: 1px solid #243247;
            }

            .av-graph-stat:last-child {
                border-bottom: none;
            }

            .av-graph-muted {
                color: #8fa2bc;
            }

            @media (max-width: 600px) {
                .av-graph-responsive {
                    padding: 12px !important;
                }
            }
        `;

        document.head.appendChild(style);
    }

    createUI() {
        const header = document.createElement("div");

        Object.assign(header.style, {
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: "12px",
            marginBottom: "18px"
        });

        const headingGroup = document.createElement("div");

        const eyebrow = document.createElement("div");
        eyebrow.textContent = "HISTORICAL WEATHER ANALYSIS";

        Object.assign(eyebrow.style, {
            color: "#55c8ff",
            fontSize: "10px",
            fontWeight: "700",
            letterSpacing: "1.1px",
            marginBottom: "5px"
        });

        const title = document.createElement("div");
        title.textContent = "Weather Graphs";

        Object.assign(title.style, {
            fontSize: "22px",
            fontWeight: "750",
            letterSpacing: "-0.3px"
        });

        const subtitle = document.createElement("div");
        subtitle.textContent =
            "Explore historical weather variables across time.";

        Object.assign(subtitle.style, {
            marginTop: "4px",
            color: "#91a1b8",
            fontSize: "12px"
        });

        headingGroup.append(eyebrow, title, subtitle);

        this.dataStatus = document.createElement("div");

        Object.assign(this.dataStatus.style, {
            padding: "6px 10px",
            border: "1px solid #344157",
            borderRadius: "5px",
            background: "#111c2b",
            color: "#9eacc2",
            fontSize: "11px"
        });

        this.dataStatus.textContent = "Waiting for ERA5 data";

        header.append(headingGroup, this.dataStatus);
        this.element.appendChild(header);

        // Selection summary
        this.selectionSummary = this.createCard();

        const selectionTitle = document.createElement("div");
        selectionTitle.textContent = "ANALYSIS TARGET";

        Object.assign(selectionTitle.style, {
            color: "#8fa2bc",
            fontSize: "10px",
            fontWeight: "700",
            letterSpacing: "0.8px",
            marginBottom: "5px"
        });

        this.selectionText = document.createElement("div");
        this.selectionText.textContent =
            "Select a point or rectangle on the geographic map.";

        Object.assign(this.selectionText.style, {
            fontWeight: "600",
            overflowWrap: "anywhere"
        });

        this.selectionDetail = document.createElement("div");
        this.selectionDetail.textContent =
            "The selected location and time range will appear here.";

        Object.assign(this.selectionDetail.style, {
            color: "#8fa2bc",
            fontSize: "11px",
            marginTop: "4px"
        });

        this.selectionSummary.append(
            selectionTitle,
            this.selectionText,
            this.selectionDetail
        );

        this.element.appendChild(this.selectionSummary);

        // Universal graph
        this.universalCard = this.createCard();
        this.universalCard.style.marginTop = "14px";

        this.addCardHeading(
            this.universalCard,
            "Universal Weather Graph",
            "Compare enabled variables over the same timeline."
        );

        this.universalDescription = document.createElement("div");

        Object.assign(this.universalDescription.style, {
            marginBottom: "10px",
            color: "#8fa2bc",
            fontSize: "11px"
        });

        this.universalDescription.textContent =
            "Variables are normalized for visual comparison. " +
            "Hover over a series to inspect actual values and units.";

        this.universalCard.appendChild(this.universalDescription);

        this.universalChart = this.createChartHost();
        this.universalCard.appendChild(this.universalChart);

        this.legend = document.createElement("div");
        this.legend.className = "av-graph-legend";
        this.universalCard.appendChild(this.legend);

        this.element.appendChild(this.universalCard);

        // Individual graphs
        const individualHeading = document.createElement("div");

        Object.assign(individualHeading.style, {
            margin: "24px 0 12px"
        });

        const individualTitle = document.createElement("div");
        individualTitle.textContent = "Individual Variables";

        Object.assign(individualTitle.style, {
            fontSize: "17px",
            fontWeight: "700"
        });

        const individualSubtitle = document.createElement("div");
        individualSubtitle.textContent =
            "Each variable has its own value scale and units.";

        Object.assign(individualSubtitle.style, {
            marginTop: "3px",
            color: "#8fa2bc",
            fontSize: "12px"
        });

        individualHeading.append(
            individualTitle,
            individualSubtitle
        );

        this.element.appendChild(individualHeading);

        this.variableGrid = document.createElement("div");
        this.variableGrid.className = "av-graph-grid";

        this.element.appendChild(this.variableGrid);

        this.variableCards = new Map();

        for (const variable of this.variables) {
            const card = this.createCard();

            this.addCardHeading(
                card,
                variable.label,
                `Historical values · ${variable.unit}`
            );

            const chart = this.createChartHost();
            card.appendChild(chart);

            const statistics = document.createElement("div");

            Object.assign(statistics.style, {
                marginTop: "8px",
                paddingTop: "8px",
                borderTop: "1px solid #293951"
            });

            card.appendChild(statistics);

            this.variableGrid.appendChild(card);

            this.variableCards.set(variable.id, {
                variable,
                card,
                chart,
                statistics
            });
        }

        // Shared readout
        this.readoutCard = this.createCard();
        this.readoutCard.style.marginTop = "14px";

        this.addCardHeading(
            this.readoutCard,
            "Data Readout",
            "Values at the selected time step."
        );

        this.readout = document.createElement("div");
        this.readout.className = "av-graph-empty";
        this.readout.textContent =
            "Historical values will appear here when data is loaded.";

        this.readoutCard.appendChild(this.readout);
        this.element.appendChild(this.readoutCard);
    }

    createCard() {
        const card = document.createElement("section");
        card.className = "av-graph-card";

        return card;
    }

    addCardHeading(card, titleText, subtitleText) {
        const heading = document.createElement("div");
        heading.className = "av-graph-heading";

        const textGroup = document.createElement("div");

        const title = document.createElement("div");
        title.className = "av-graph-title";
        title.textContent = titleText;

        const subtitle = document.createElement("div");
        subtitle.className = "av-graph-subtitle";
        subtitle.textContent = subtitleText;

        textGroup.append(title, subtitle);
        heading.appendChild(textGroup);
        card.appendChild(heading);
    }

    createChartHost() {
        const host = document.createElement("div");
        host.className = "av-graph-empty";

        host.textContent =
            "No data loaded yet. Select a location and fetch historical data.";

        return host;
    }

    setSelection(selection) {
        if (!selection) {
            this.selectionText.textContent =
                "No geographic selection";

            this.selectionDetail.textContent =
                "Choose a point or draw a rectangle on the map.";

            return;
        }

        if (selection.type === "point") {
            this.selectionText.textContent = "Point selection";

            this.selectionDetail.textContent =
                `Latitude ${selection.latitude.toFixed(4)}°, ` +
                `longitude ${selection.longitude.toFixed(4)}°`;
        } else if (selection.type === "region") {
            const bounds = selection.bounds;

            this.selectionText.textContent = "Regional average";

            this.selectionDetail.textContent =
                `Lat ${bounds.minLatitude.toFixed(3)}° to ` +
                `${bounds.maxLatitude.toFixed(3)}° · ` +
                `Lon ${bounds.minLongitude.toFixed(3)}° to ` +
                `${bounds.maxLongitude.toFixed(3)}°`;
        }
    }

    setData(data) {
        if (!data || !Array.isArray(data.timestamps)) {
            throw new TypeError(
                "setData expects a timestamps array and a series array."
            );
        }

        if (!Array.isArray(data.series)) {
            throw new TypeError(
                "setData expects series: [{ id, values }]."
            );
        }

        this.timestamps = data.timestamps;
        this.series = data.series.map(item => ({
            ...item,
            values: Array.isArray(item.values)
                ? item.values
                : []
        }));

        for (const item of this.series) {
            if (!this.enabledVariables.has(item.id)) {
                this.enabledVariables.add(item.id);
            }
        }

        this.dataStatus.textContent =
            `${this.timestamps.length} time steps`;

        this.render();
    }

    setLoading(loading = true) {
        this.dataStatus.textContent = loading
            ? "Loading historical data…"
            : `${this.timestamps.length} time steps`;
    }

    setError(message) {
        this.dataStatus.textContent = "Data request failed";

        this.readout.className = "av-graph-empty";
        this.readout.textContent = message;
    }

    render() {
        this.renderLegend();
        this.renderUniversalGraph();

        for (const [id, entry] of this.variableCards) {
            const series = this.series.find(item => item.id === id);

            this.renderIndividualGraph(
                entry,
                series
            );
        }

        if (!this.timestamps.length || !this.series.length) {
            this.dataStatus.textContent = "Waiting for ERA5 data";
        } else {
            this.dataStatus.textContent =
                `${this.timestamps.length} time steps · ` +
                `${this.series.length} variables`;
        }
    }

    renderLegend() {
        this.legend.replaceChildren();

        for (const variable of this.variables) {
            const series = this.series.find(
                item => item.id === variable.id
            );

            if (!series) {
                continue;
            }

            const button = document.createElement("button");
            button.type = "button";
            button.className = "av-graph-toggle";

            const enabled = this.enabledVariables.has(variable.id);
            button.setAttribute("aria-pressed", String(enabled));

            const swatch = document.createElement("span");

            Object.assign(swatch.style, {
                width: "8px",
                height: "8px",
                flex: "0 0 8px",
                borderRadius: "50%",
                background: this.colorFor(series)
            });

            const label = document.createElement("span");
            label.textContent = variable.label;

            button.append(swatch, label);

            button.addEventListener("click", () => {
                if (this.enabledVariables.has(variable.id)) {
                    this.enabledVariables.delete(variable.id);
                } else {
                    this.enabledVariables.add(variable.id);
                }

                this.render();
            });

            this.legend.appendChild(button);
        }
    }

    renderUniversalGraph() {
        const active = this.series.filter(
            item => this.enabledVariables.has(item.id)
        );

        if (!this.timestamps.length || !active.length) {
            this.showEmpty(
                this.universalChart,
                active.length
                    ? "No historical data loaded yet."
                    : "Enable at least one variable in the legend."
            );
            return;
        }

        this.universalChart.replaceChildren();

        const svg = this.createSVG(900, 280);
        const plot = { left: 64, right: 18, top: 18, bottom: 48 };
        const width = 900 - plot.left - plot.right;
        const height = 280 - plot.top - plot.bottom;

        this.drawGrid(svg, plot, width, height, 5);

        for (const item of active) {
            const values = item.values.map(Number);
            const valid = values.filter(Number.isFinite);

            if (!valid.length) {
                continue;
            }

            const min = Math.min(...valid);
            const max = Math.max(...valid);
            const span = max - min || 1;

            const normalized = values.map(value =>
                Number.isFinite(value)
                    ? (value - min) / span
                    : null
            );

            this.drawSeries(
                svg,
                normalized,
                item,
                plot,
                width,
                height,
                { min, max, normalized: true }
            );
        }

        this.drawTimeLabels(svg, plot, width, height);
        this.attachHover(svg, plot, width, height, active);

        this.universalChart.appendChild(svg);
    }

    renderIndividualGraph(entry, series) {
        if (!this.timestamps.length || !series) {
            this.showEmpty(
                entry.chart,
                "No historical data loaded for this variable."
            );

            entry.statistics.replaceChildren();
            return;
        }

        const values = series.values.map(value =>
            value === null || value === undefined || value === ""
                ? null
                : Number(value)
        );

        const valid = values.filter(Number.isFinite);

        if (!valid.length) {
            this.showEmpty(
                entry.chart,
                "No valid observations for this variable."
            );

            entry.statistics.replaceChildren();
            return;
        }

        entry.chart.replaceChildren();

        const svg = this.createSVG(600, 220);
        const plot = { left: 56, right: 14, top: 16, bottom: 40 };
        const width = 600 - plot.left - plot.right;
        const height = 220 - plot.top - plot.bottom;

        const min = Math.min(...valid);
        const max = Math.max(...valid);
        const padding = (max - min || Math.max(Math.abs(max), 1)) * 0.08;

        const low = min - padding;
        const high = max + padding;

        this.drawGrid(
            svg,
            plot,
            width,
            height,
            4,
            low,
            high,
            entry.variable.unit
        );

        this.drawSeries(
            svg,
            values,
            series,
            plot,
            width,
            height,
            { min: low, max: high }
        );

        this.drawTimeLabels(svg, plot, width, height);
        this.attachHover(svg, plot, width, height, [series]);

        entry.chart.appendChild(svg);

        const mean = valid.reduce((sum, value) => sum + value, 0) /
            valid.length;

        const stats = [
            ["Minimum", min],
            ["Average", mean],
            ["Maximum", max]
        ];

        entry.statistics.replaceChildren();

        for (const [label, value] of stats) {
            const row = document.createElement("div");
            row.className = "av-graph-stat";

            const name = document.createElement("span");
            name.className = "av-graph-muted";
            name.textContent = label;

            const number = document.createElement("strong");
            number.textContent =
                `${this.formatValue(value)} ${entry.variable.unit}`;

            row.append(name, number);
            entry.statistics.appendChild(row);
        }
    }

    createSVG(width, height) {
        const svg = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "svg"
        );

        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        svg.setAttribute("class", "av-graph-svg");
        svg.setAttribute("role", "img");
        svg.setAttribute("aria-label", "Historical weather time series");

        return svg;
    }

    drawGrid(svg, plot, width, height, divisions, min, max, unit = "") {
        const ns = "http://www.w3.org/2000/svg";

        for (let i = 0; i <= divisions; i++) {
            const y = plot.top + (height * i) / divisions;

            const line = document.createElementNS(ns, "line");
            line.setAttribute("x1", plot.left);
            line.setAttribute("x2", plot.left + width);
            line.setAttribute("y1", y);
            line.setAttribute("y2", y);
            line.setAttribute("stroke", "#253449");
            line.setAttribute("stroke-width", "1");

            svg.appendChild(line);

            const label = document.createElementNS(ns, "text");
            label.setAttribute("x", plot.left - 9);
            label.setAttribute("y", y + 4);
            label.setAttribute("text-anchor", "end");
            label.setAttribute("fill", "#8395ad");
            label.setAttribute("font-size", "10");

            if (Number.isFinite(min) && Number.isFinite(max)) {
                const value = max - ((max - min) * i) / divisions;
                label.textContent = this.formatValue(value);
            } else {
                label.textContent = `${100 - i * (100 / divisions)}%`;
            }

            svg.appendChild(label);
        }

        const axisLabel = document.createElementNS(ns, "text");
        axisLabel.setAttribute("x", plot.left);
        axisLabel.setAttribute("y", 11);
        axisLabel.setAttribute("fill", "#8395ad");
        axisLabel.setAttribute("font-size", "10");
        axisLabel.textContent = unit
            ? `Value (${unit})`
            : "Relative scale";

        svg.appendChild(axisLabel);
    }

    drawTimeLabels(svg, plot, width, height) {
        if (!this.timestamps.length) {
            return;
        }

        const ns = "http://www.w3.org/2000/svg";
        const count = this.timestamps.length;
        const labels = Math.min(5, count);

        for (let i = 0; i < labels; i++) {
            const index = labels === 1
                ? 0
                : Math.round((i * (count - 1)) / (labels - 1));

            const x = count === 1
                ? plot.left + width / 2
                : plot.left + (index / (count - 1)) * width;

            const text = document.createElementNS(ns, "text");
            text.setAttribute("x", x);
            text.setAttribute("y", plot.top + height + 22);
            text.setAttribute(
                "text-anchor",
                i === 0
                    ? "start"
                    : i === labels - 1
                        ? "end"
                        : "middle"
            );
            text.setAttribute("fill", "#8395ad");
            text.setAttribute("font-size", "10");
            text.textContent = this.formatTime(this.timestamps[index]);

            svg.appendChild(text);
        }

        const axisTitle = document.createElementNS(ns, "text");
        axisTitle.setAttribute("x", plot.left + width / 2);
        axisTitle.setAttribute("y", plot.top + height + 39);
        axisTitle.setAttribute("text-anchor", "middle");
        axisTitle.setAttribute("fill", "#8395ad");
        axisTitle.setAttribute("font-size", "10");
        axisTitle.textContent = "Time (UTC)";

        svg.appendChild(axisTitle);
    }

    drawSeries(svg, values, series, plot, width, height, scale) {
        const ns = "http://www.w3.org/2000/svg";
        const count = values.length;

        if (!count) {
            return;
        }

        const points = values.map((value, index) => {
            if (!Number.isFinite(value)) {
                return null;
            }

            const x = count === 1
                ? plot.left + width / 2
                : plot.left + (index / (count - 1)) * width;

            const range = scale.max - scale.min || 1;
            const y = plot.top +
                height * (1 - (value - scale.min) / range);

            return { x, y, value, index };
        });

        let pathData = "";
        let drawing = false;

        for (const point of points) {
            if (!point) {
                drawing = false;
                continue;
            }

            pathData +=
                `${drawing ? " L" : " M"}${point.x},${point.y}`;

            drawing = true;
        }

        if (!pathData) {
            return;
        }

        const path = document.createElementNS(ns, "path");
        path.setAttribute("d", pathData);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", this.colorFor(series));
        path.setAttribute("stroke-width", "1.8");
        path.setAttribute("stroke-linejoin", "round");
        path.setAttribute("stroke-linecap", "round");

        svg.appendChild(path);

        if (count === 1 && points[0]) {
            const circle = document.createElementNS(ns, "circle");
            circle.setAttribute("cx", points[0].x);
            circle.setAttribute("cy", points[0].y);
            circle.setAttribute("r", "3.5");
            circle.setAttribute("fill", this.colorFor(series));

            svg.appendChild(circle);
        }
    }

    attachHover(svg, plot, width, height, activeSeries) {
        const ns = "http://www.w3.org/2000/svg";

        const overlay = document.createElementNS(ns, "rect");
        overlay.setAttribute("x", plot.left);
        overlay.setAttribute("y", plot.top);
        overlay.setAttribute("width", width);
        overlay.setAttribute("height", height);
        overlay.setAttribute("fill", "transparent");
        overlay.setAttribute("pointer-events", "all");
        overlay.style.cursor = "crosshair";

        const guide = document.createElementNS(ns, "line");
        guide.setAttribute("y1", plot.top);
        guide.setAttribute("y2", plot.top + height);
        guide.setAttribute("stroke", "#e8edf7");
        guide.setAttribute("stroke-opacity", "0.45");
        guide.setAttribute("stroke-dasharray", "3 4");
        guide.style.display = "none";
        guide.setAttribute("pointer-events", "none");

        overlay.addEventListener("pointermove", event => {
            const rect = svg.getBoundingClientRect();
            const viewBox = svg.viewBox.baseVal;

            const localX =
                ((event.clientX - rect.left) / rect.width) * viewBox.width;

            const count = this.timestamps.length;

            if (!count) {
                return;
            }

            const fraction = Math.max(
                0,
                Math.min(1, (localX - plot.left) / width)
            );

            const index = count === 1
                ? 0
                : Math.round(fraction * (count - 1));

            const x = count === 1
                ? plot.left + width / 2
                : plot.left + (index / (count - 1)) * width;

            guide.setAttribute("x1", x);
            guide.setAttribute("x2", x);
            guide.style.display = "";

            this.updateReadout(index, activeSeries);
        });

        overlay.addEventListener("pointerleave", () => {
            guide.style.display = "none";
        });

        svg.append(guide, overlay);
    }

    updateReadout(index, activeSeries) {
        this.readout.className = "";
        this.readout.classList.add("av-graph-tooltip");
        this.readout.replaceChildren();

        const timestamp = document.createElement("div");

        Object.assign(timestamp.style, {
            fontWeight: "700",
            marginBottom: "7px"
        });

        timestamp.textContent = this.formatTime(
            this.timestamps[index]
        );

        this.readout.appendChild(timestamp);

        for (const item of activeSeries) {
            const value = item.values[index];
            const row = document.createElement("div");
            row.className = "av-graph-stat";

            const label = document.createElement("span");
            label.style.color = this.colorFor(item);
            label.textContent = item.label ?? item.id;

            const result = document.createElement("strong");
            result.textContent =
                value === null ||
                value === undefined ||
                value === "" ||
                !Number.isFinite(Number(value))
                    ? "No data"
                    : `${this.formatValue(Number(value))} ${item.unit ?? ""}`;

            row.append(label, result);
            this.readout.appendChild(row);
        }
    }

    showEmpty(host, message) {
        host.replaceChildren();
        host.className = "av-graph-empty";
        host.textContent = message;
    }

    colorFor(series) {
        return series.color ??
            GRAPH_COLORS[series.id] ??
            "#55c8ff";
    }

    formatValue(value) {
        if (!Number.isFinite(value)) {
            return "—";
        }

        return new Intl.NumberFormat("en", {
            maximumFractionDigits: 2
        }).format(value);
    }

    formatTime(value) {
        if (typeof value === "number") {
            value = new Date(value);
        } else if (typeof value === "string") {
            value = new Date(value);
        }

        if (value instanceof Date && !Number.isNaN(value.getTime())) {
            return value.toISOString().replace("T", " ").slice(0, 16);
        }

        return String(value);
    }

    setStatus(message) {
        this.dataStatus.textContent = message;
    }

    destroy() {
        this.element.remove();
    }
}
