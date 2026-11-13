
export class ScientificAnalysisPanel {
    constructor(container, onRunAnalysis) {
        this.onRunAnalysis = onRunAnalysis;
        this.selection = null;

        this.element = document.createElement("section");

        Object.assign(this.element.style, {
            margin: "12px",
            padding: "16px",
            background: "#0c121e",
            color: "#e8edf7",
            border: "1px solid #344157",
            borderRadius: "8px",
            font: "13px/1.5 system-ui, sans-serif",
            boxSizing: "border-box"
        });

        this.element.innerHTML = `
            <h3 style="margin:0 0 12px">
                Scientific Analysis
            </h3>

            <p style="color:#aab7cc;margin:0 0 14px">
                Detect weather anomalies and follow their
                evolution across the analysis period.
            </p>

            <div class="analysis-grid"
                 style="display:grid;grid-template-columns:
                 repeat(auto-fit,minmax(210px,1fr));gap:12px">

                <label>
                    Weather variable
                    <select name="variable" style="width:100%">
                        <option value="temperature">Temperature</option>
                        <option value="dewpoint">Dewpoint</option>
                        <option value="mean_sea_level_pressure">
                            Mean Sea Level Pressure
                        </option>
                        <option value="surface_pressure">
                            Surface Pressure
                        </option>
                        <option value="wind_u">U Wind Component</option>
                        <option value="wind_v">V Wind Component</option>
                        <option value="total_precipitation">
                            Total Precipitation
                        </option>
                    </select>
                </label>

                <label>
                    Analysis interval (hours)
                    <select name="interval" style="width:100%">
                        <option value="6" selected>6 hours</option>
                        <option value="12">12 hours</option>
                        <option value="24">24 hours</option>
                    </select>
                </label>

                <label>
                    Minimum latitude
                    <input name="minLatitude" type="number"
                        min="-90" max="90" step="any" value="-90"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Maximum latitude
                    <input name="maxLatitude" type="number"
                        min="-90" max="90" step="any" value="90"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Minimum longitude
                    <input name="minLongitude" type="number"
                        min="-180" max="180" step="any" value="-180"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Maximum longitude
                    <input name="maxLongitude" type="number"
                        min="-180" max="180" step="any" value="180"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Baseline start
                    <input name="baselineStart" type="datetime-local"
                        value="2015-01-01T00:00"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Baseline end
                    <input name="baselineEnd" type="datetime-local"
                        value="2018-12-31T18:00"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Analysis start
                    <input name="analysisStart" type="datetime-local"
                        value="2019-07-01T00:00"
                        style="width:100%;box-sizing:border-box">
                </label>

                <label>
                    Analysis end
                    <input name="analysisEnd" type="datetime-local"
                        value="2019-07-15T18:00"
                        style="width:100%;box-sizing:border-box">
                </label>
            </div>

            <div style="display:flex;gap:10px;align-items:center;
                        flex-wrap:wrap;margin-top:16px">
                <button type="button" data-action="run"
                    style="padding:9px 14px;cursor:pointer">
                    Run Analysis
                </button>

                <span data-role="status"
                    style="color:#aab7cc">
                    Ready
                </span>
            </div>

            <div data-role="summary"
                style="margin-top:14px"></div>
        `;

        container.appendChild(this.element);

        this.statusElement =
            this.element.querySelector('[data-role="status"]');

        this.summaryElement =
            this.element.querySelector('[data-role="summary"]');

        this.runButton =
            this.element.querySelector('[data-action="run"]');

        this.runButton.addEventListener("click", async () => {
            try {
                const request = this.getRequest();

                this.setBusy(true);
                this.setStatus("Running scientific analysis...");

                const result = await this.onRunAnalysis(request);

                this.showSummary(result);
                this.setStatus("Analysis completed.");
            } catch (error) {
                this.setStatus(`Analysis failed: ${error.message}`);
                console.error("[Scientific Analysis]", error);
            } finally {
                this.setBusy(false);
            }
        });
    }

    getInput(name) {
        return this.element.querySelector(`[name="${name}"]`);
    }

    getRequest() {
        const number = name => {
            const value = Number(this.getInput(name).value);

            if (!Number.isFinite(value)) {
                throw new Error(`Invalid value for ${name}.`);
            }

            return value;
        };

        const text = name => this.getInput(name).value;

        const request = {
            variable: text("variable"),

            min_latitude: number("minLatitude"),
            max_latitude: number("maxLatitude"),
            min_longitude: number("minLongitude"),
            max_longitude: number("maxLongitude"),

            baseline_start_time: text("baselineStart"),
            baseline_end_time: text("baselineEnd"),

            analysis_start_time: text("analysisStart"),
            analysis_end_time: text("analysisEnd"),

            interval_hours: number("interval")
        };

        if (request.min_latitude > request.max_latitude) {
            throw new Error("Minimum latitude exceeds maximum latitude.");
        }

        if (request.min_longitude > request.max_longitude) {
            throw new Error("Minimum longitude exceeds maximum longitude.");
        }

        if (request.baseline_start_time > request.baseline_end_time) {
            throw new Error("Invalid baseline time range.");
        }

        if (request.analysis_start_time > request.analysis_end_time) {
            throw new Error("Invalid analysis time range.");
        }

        return request;
    }

    setSelection(selection) {
        this.selection = selection;

        if (!selection) {
            return;
        }

        let bounds;

        if (selection.type === "region") {
            bounds = selection.bounds;
        } else if (selection.type === "point") {
            bounds = {
                minLatitude: selection.latitude,
                maxLatitude: selection.latitude,
                minLongitude: selection.longitude,
                maxLongitude: selection.longitude
            };
        } else {
            return;
        }

        this.getInput("minLatitude").value = bounds.minLatitude;
        this.getInput("maxLatitude").value = bounds.maxLatitude;
        this.getInput("minLongitude").value = bounds.minLongitude;
        this.getInput("maxLongitude").value = bounds.maxLongitude;
    }

    setBusy(busy) {
        this.runButton.disabled = busy;
        this.runButton.textContent =
            busy ? "Analyzing..." : "Run Analysis";
    }

    setStatus(message) {
        this.statusElement.textContent = message;
    }

    
showSummary(result) {
    if (!result || typeof result !== "object") {
        throw new Error("The analysis API returned an invalid result.");
    }

    this.summaryElement.replaceChildren();

    const root = document.createElement("div");

    Object.assign(root.style, {
        display: "grid",
        gap: "14px",
        marginTop: "14px"
    });

    const heading = document.createElement("h4");
    heading.textContent = "Analysis Results";
    heading.style.margin = "0";
    root.appendChild(heading);

    const frames = Array.isArray(result.frames) ? result.frames : [];
    const tracks = Array.isArray(result.tracks) ? result.tracks : [];
    const events = Array.isArray(result.events) ? result.events : [];

    const frameCount = result.frame_count ?? frames.length;
    const trackCount = result.track_count ?? tracks.length;
    const eventCount = result.event_count ?? events.length;

    const countItems = [
        ["Variable", result.variable ?? "Unknown"],
        ["Frames", frameCount],
        ["Tracks", trackCount],
        ["Events", eventCount]
    ];

    const cards = document.createElement("div");

    Object.assign(cards.style, {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
        gap: "8px"
    });

    for (const [label, value] of countItems) {
        const card = document.createElement("div");

        Object.assign(card.style, {
            padding: "12px",
            background: "#151f30",
            border: "1px solid #344157",
            borderRadius: "6px"
        });

        const caption = document.createElement("div");
        caption.textContent = label;
        caption.style.color = "#aab7cc";

        const number = document.createElement("div");
        number.textContent = String(value);
        Object.assign(number.style, {
            fontSize: "20px",
            fontWeight: "600",
            overflowWrap: "anywhere"
        });

        card.append(caption, number);
        cards.appendChild(card);
    }

    root.appendChild(cards);

    const section = (title) => {
        const wrapper = document.createElement("section");

        const heading = document.createElement("h4");
        heading.textContent = title;
        heading.style.margin = "0 0 8px";

        wrapper.appendChild(heading);
        root.appendChild(wrapper);

        return wrapper;
    };

    const formatValue = (value) => {
        if (value === null || value === undefined) {
            return "—";
        }

        if (typeof value === "object") {
            return JSON.stringify(value);
        }

        return String(value);
    };

    const getTimestamp = (frame) =>
        frame.time ??
        frame.timestamp ??
        frame.datetime ??
        frame.valid_time ??
        "Unknown timestamp";

    const getCount = (frame, names) => {
        for (const name of names) {
            const value = frame[name];

            if (typeof value === "number") {
                return value;
            }

            if (Array.isArray(value)) {
                return value.length;
            }

            if (value && typeof value === "object") {
                // Prefer explicit count fields if the data is an object.
                for (const key of ["count", "total", "length"]) {
                    if (typeof value[key] === "number") {
                        return value[key];
                    }
                }
            }
        }

        return null;
    };

    // Timestamp-by-timestamp results.
    const frameSection = section("Timestamp Breakdown");

    if (frames.length === 0) {
        const message = document.createElement("p");
        message.textContent =
            "The API returned no frames. Inspect the response details below.";
        message.style.color = "#aab7cc";
        frameSection.appendChild(message);
    } else {
        const table = document.createElement("table");

        Object.assign(table.style, {
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "12px"
        });

        const header = document.createElement("tr");

        for (const text of ["Timestamp", "Anomalies", "Regions"]) {
            const th = document.createElement("th");
            th.textContent = text;

            Object.assign(th.style, {
                textAlign: "left",
                padding: "8px 5px",
                borderBottom: "1px solid #344157"
            });

            header.appendChild(th);
        }

        const thead = document.createElement("thead");
        thead.appendChild(header);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");

        frames.forEach((frame, index) => {
            const tr = document.createElement("tr");

            const anomalyCount = getCount(frame, [
                "anomaly_count",
                "anomalies_count",
                "anomalies",
                "anomaly_field",
                "anomalyField"
            ]);

            const regionCount = getCount(frame, [
                "region_count",
                "regions_count",
                "regions",
                "region_field",
                "regionField"
            ]);

            const values = [
                getTimestamp(frame),
                anomalyCount === null ? "See frame data" : anomalyCount,
                regionCount === null ? "See frame data" : regionCount
            ];

            for (const value of values) {
                const td = document.createElement("td");
                td.textContent = formatValue(value);

                Object.assign(td.style, {
                    padding: "8px 5px",
                    borderBottom: "1px solid #253247",
                    overflowWrap: "anywhere"
                });

                tr.appendChild(td);
            }

            tbody.appendChild(tr);

            // Keep the index for the matching expandable frame below.
            frame._panelIndex = index;
        });

        table.appendChild(tbody);
        frameSection.appendChild(table);

        const frameDetails = document.createElement("details");
        frameDetails.style.marginTop = "10px";

        const summary = document.createElement("summary");
        summary.textContent = "Inspect raw frame data";
        summary.style.cursor = "pointer";
        frameDetails.appendChild(summary);

        const frameSelect = document.createElement("select");

        Object.assign(frameSelect.style, {
            display: "block",
            width: "100%",
            marginTop: "8px",
            padding: "7px",
            background: "#151f30",
            color: "#e8edf7",
            border: "1px solid #344157"
        });

        frames.forEach((frame, index) => {
            const option = document.createElement("option");
            option.value = String(index);
            option.textContent = `${index + 1}. ${getTimestamp(frame)}`;
            frameSelect.appendChild(option);
        });

        const frameJson = document.createElement("pre");

        Object.assign(frameJson.style, {
            whiteSpace: "pre-wrap",
            overflowWrap: "anywhere",
            maxHeight: "350px",
            overflow: "auto",
            padding: "10px",
            background: "#080d15",
            borderRadius: "5px",
            fontSize: "11px"
        });

        const updateFrame = () => {
            frameJson.textContent = JSON.stringify(
                frames[Number(frameSelect.value)],
                null,
                2
            );
        };

        frameSelect.addEventListener("change", updateFrame);
        frameDetails.append(frameSelect, frameJson);
        frameSection.appendChild(frameDetails);

        updateFrame();
    }

    // Track details.
    const trackSection = section(`Tracks (${trackCount})`);

    if (tracks.length === 0) {
        const message = document.createElement("p");
        message.textContent = "No tracks were returned for this analysis.";
        message.style.color = "#aab7cc";
        trackSection.appendChild(message);
    } else {
        const list = document.createElement("div");

        tracks.forEach((track, index) => {
            const details = document.createElement("details");
            details.style.marginBottom = "8px";

            const summary = document.createElement("summary");
            summary.textContent =
                `Track ${index + 1}: ${track.category ?? "Unclassified"}`;

            summary.style.cursor = "pointer";

            const pre = document.createElement("pre");
            pre.textContent = JSON.stringify(track, null, 2);

            Object.assign(pre.style, {
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
                fontSize: "11px"
            });

            details.append(summary, pre);
            list.appendChild(details);
        });

        trackSection.appendChild(list);
    }

    // Event details.
    const eventSection = section(`Events (${eventCount})`);

    if (events.length === 0) {
        const message = document.createElement("p");
        message.textContent = "No events were returned for this analysis.";
        message.style.color = "#aab7cc";
        eventSection.appendChild(message);
    } else {
        events.forEach((event, index) => {
            const details = document.createElement("details");
            details.style.marginBottom = "8px";

            const summary = document.createElement("summary");
            summary.textContent =
                `Event ${index + 1}: ${event.category ?? "Unclassified"}`;

            summary.style.cursor = "pointer";

            const pre = document.createElement("pre");
            pre.textContent = JSON.stringify(event, null, 2);

            Object.assign(pre.style, {
                whiteSpace: "pre-wrap",
                overflowWrap: "anywhere",
                fontSize: "11px"
            });

            details.append(summary, pre);
            eventSection.appendChild(details);
        });
    }

    // Full response for debugging any unexpected schema.
    const rawSection = section("Full API Response");
    const rawDetails = document.createElement("details");
    const rawSummary = document.createElement("summary");

    rawSummary.textContent = "Expand complete JSON response";
    rawSummary.style.cursor = "pointer";

    const rawJson = document.createElement("pre");
    rawJson.textContent = JSON.stringify(result, null, 2);

    Object.assign(rawJson.style, {
        whiteSpace: "pre-wrap",
        overflowWrap: "anywhere",
        maxHeight: "400px",
        overflow: "auto",
        padding: "10px",
        background: "#080d15",
        borderRadius: "5px",
        fontSize: "11px"
    });

    rawDetails.append(rawSummary, rawJson);
    rawSection.appendChild(rawDetails);

    this.summaryElement.appendChild(root);
}

}
