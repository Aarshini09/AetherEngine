
import L from "leaflet";
import "leaflet-draw";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";

export class GeographicSelectionPanel {
    constructor(container, onSelectionChange, mapComponent, onFetchData) {
        if (!mapComponent?.map || !mapComponent?.mapElement) {
            throw new Error(
                "GeographicSelectionPanel requires an existing GeographicMap."
            );
        }

        this.container = container;
        this.onSelectionChange = onSelectionChange;
        this.onFetchData = onFetchData;
        this.mapComponent = mapComponent;
        this.map = mapComponent.map;
        this.mapElement = mapComponent.mapElement;

        this.currentSelection = null;
        this.selectionMode = "point";
        this.selectionLayer = null;
        this.marker = null;
        this.rectangleDrawer = null;
        this.editToolbar = null;
        this.destroyed = false;

        this.drawnItems = new L.FeatureGroup();

        this.handleMapClick = this.handleMapClick.bind(this);
        this.handleMouseMove = this.handleMouseMove.bind(this);
        this.handleRectangleCreated =
            this.handleRectangleCreated.bind(this);
        this.handleRectangleEdited =
            this.handleRectangleEdited.bind(this);
        this.handleRectangleEditStart =
            this.handleRectangleEditStart.bind(this);
        this.handleRectangleEditStop =
            this.handleRectangleEditStop.bind(this);

        this.createUI();
        this.configureMap();
    }

    createUI() {
        this.element = document.createElement("section");

        Object.assign(this.element.style, {
            width: "calc(100% - 32px)",
            maxWidth: "1568px",
            boxSizing: "border-box",
            margin: "24px auto",
            padding: "20px",
            background: "#0c121e",
            color: "#e8edf7",
            border: "1px solid #344157",
            borderRadius: "10px",
            font: "13px/1.5 system-ui, sans-serif"
        });

        // Header
        const header = document.createElement("div");

        Object.assign(header.style, {
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "8px",
            marginBottom: "16px"
        });

        const headingGroup = document.createElement("div");
        const title = document.createElement("div");

        title.textContent = "Geographic Area Selection";

        Object.assign(title.style, {
            fontSize: "19px",
            fontWeight: "700",
            letterSpacing: "0.2px"
        });

        const description = document.createElement("div");

        description.textContent =
            "Define a geographic area for historical weather analysis.";

        Object.assign(description.style, {
            marginTop: "3px",
            color: "#9eacc2",
            fontSize: "12px"
        });

        headingGroup.append(title, description);
        header.appendChild(headingGroup);
        this.element.appendChild(header);

        // 1. Find a location
        this.element.appendChild(
            this.makeLabel("FIND A LOCATION")
        );

        this.searchInput = document.createElement("input");
        this.searchInput.type = "search";
        this.searchInput.placeholder =
            "Search for a city, region, or place...";
        this.searchInput.setAttribute(
            "aria-label",
            "Search for a location"
        );

        Object.assign(this.searchInput.style, this.controlStyle(), {
            flex: "1 1 240px",
            minWidth: "0"
        });

        this.searchButton = this.makeButton(
            "Search",
            "#3679d8"
        );

        const searchRow = this.makeRow();

        searchRow.append(
            this.searchInput,
            this.searchButton
        );

        this.element.appendChild(searchRow);

        this.searchButton.addEventListener("click", () => {
            this.searchPlace();
        });

        this.searchInput.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                this.searchPlace();
            }
        });

        // 2. Always-visible coordinate editor
        this.element.appendChild(
            this.makeLabel("CUSTOM GEOGRAPHIC COORDINATES")
        );

        const coordinateDescription = document.createElement("div");

        coordinateDescription.textContent =
            "Enter the minimum and maximum latitude and longitude. " +
            "Apply the values to position and size the highlighted region.";

        Object.assign(coordinateDescription.style, {
            color: "#9eacc2",
            fontSize: "12px",
            marginBottom: "10px"
        });

        this.element.appendChild(coordinateDescription);

        const coordinatePanel = document.createElement("div");

        Object.assign(coordinatePanel.style, {
            padding: "14px",
            marginBottom: "16px",
            background: "#111c2b",
            border: "1px solid #344157",
            borderRadius: "8px"
        });

        const coordinateGrid = document.createElement("div");

        Object.assign(coordinateGrid.style, {
            display: "grid",
            gridTemplateColumns:
                "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "12px"
        });

        this.minLatInput = this.makeNumberInput(
            "Minimum latitude (South)",
            -90,
            90,
            20
        );

        this.maxLatInput = this.makeNumberInput(
            "Maximum latitude (North)",
            -90,
            90,
            25
        );

        this.minLonInput = this.makeNumberInput(
            "Minimum longitude (West)",
            -180,
            180,
            75
        );

        this.maxLonInput = this.makeNumberInput(
            "Maximum longitude (East)",
            -180,
            180,
            80
        );

        for (const field of [
            this.minLatInput,
            this.maxLatInput,
            this.minLonInput,
            this.maxLonInput
        ]) {
            coordinateGrid.appendChild(field.wrapper);
        }

        this.applyCoordinatesButton = this.makeButton(
            "Apply Coordinates",
            "#3679d8"
        );

        Object.assign(this.applyCoordinatesButton.style, {
            marginTop: "12px"
        });

        this.coordinateMessage = document.createElement("div");

        Object.assign(this.coordinateMessage.style, {
            color: "#9eacc2",
            fontSize: "11px",
            marginTop: "8px"
        });

        this.coordinateMessage.textContent =
            "The coordinate fields update when you draw or resize a rectangle.";

        coordinatePanel.append(
            coordinateGrid,
            this.applyCoordinatesButton,
            this.coordinateMessage
        );

        this.element.appendChild(coordinatePanel);

        this.applyCoordinatesButton.addEventListener("click", () => {
            this.applyCustomCoordinates();
        });

        // 3. Selection tools
        this.element.appendChild(
            this.makeLabel("MAP SELECTION TOOLS")
        );

        const toolbar = this.makeRow();

        this.pointButton = this.makeButton(
            "Select Point",
            "#202f45"
        );

        this.regionButton = this.makeButton(
            "Draw Rectangle",
            "#202f45"
        );

        this.editButton = this.makeButton(
            "Resize Rectangle",
            "#202f45"
        );

        this.clearButton = this.makeButton(
            "Clear Selection",
            "#202f45"
        );

        this.fetchButton = this.makeButton(
            "Fetch Data",
            "#176b55"
        );

        this.editButton.disabled = true;
        this.fetchButton.disabled = true;

        toolbar.append(
            this.pointButton,
            this.regionButton,
            this.editButton,
            this.clearButton,
            this.fetchButton
        );

        this.element.appendChild(toolbar);

        this.pointButton.addEventListener("click", () => {
            this.setSelectionMode("point");
        });

        this.regionButton.addEventListener("click", () => {
            this.setSelectionMode("region");
        });

        this.editButton.addEventListener("click", () => {
            this.toggleRectangleEditing();
        });

        this.clearButton.addEventListener("click", () => {
            this.clearSelection();
        });

        this.fetchButton.addEventListener("click", () => {
            this.fetchSelectedData();
        });

        // 4. Live cursor coordinates
        this.cursorCoordinates = document.createElement("div");

        Object.assign(this.cursorCoordinates.style, {
            padding: "10px 12px",
            marginBottom: "10px",
            background: "#111c2b",
            border: "1px solid #293951",
            borderRadius: "6px",
            color: "#cbd5e4",
            fontVariantNumeric: "tabular-nums"
        });

        this.cursorCoordinates.textContent =
            "Cursor: move over the map to inspect latitude and longitude.";

        this.element.appendChild(this.cursorCoordinates);

        // 5. Existing map
        Object.assign(this.mapElement.style, {
            display: "block",
            width: "100%",
            height: "480px",
            boxSizing: "border-box",
            border: "1px solid #344157",
            borderRadius: "7px",
            overflow: "hidden",
            background: "#182235"
        });

        this.element.appendChild(this.mapElement);

        // Status
        this.statusText = document.createElement("div");

        Object.assign(this.statusText.style, {
            marginTop: "12px",
            padding: "10px 12px",
            border: "1px solid #293951",
            borderRadius: "6px",
            background: "#111c2b",
            color: "#cbd5e4",
            overflowWrap: "anywhere"
        });

        this.statusText.textContent =
            "Enter custom coordinates or choose a selection tool.";

        this.element.appendChild(this.statusText);

        // Regional weather statistics
        this.regionalStatisticsElement = document.createElement("div");

        Object.assign(this.regionalStatisticsElement.style, {
            display: "none",
            marginTop: "16px",
            padding: "16px",
            background: "#111c2b",
            border: "1px solid #344157",
            borderRadius: "8px",
            overflowX: "auto"
        });

        this.element.appendChild(this.regionalStatisticsElement);

        this.container.appendChild(this.element);

        this.updateButtons();
    }

    configureMap() {
        this.map.addLayer(this.drawnItems);

        this.rectangleDrawer = new L.Draw.Rectangle(this.map, {
            shapeOptions: {
                color: "#39a7ff",
                weight: 3,
                opacity: 1,
                fill: true,
                fillColor: "#2787ed",
                fillOpacity: 0.24,
                interactive: false
            },
            showArea: true
        });

        this.map.on("click", this.handleMapClick);
        this.map.on("mousemove", this.handleMouseMove);

        this.map.on(
            L.Draw.Event.CREATED,
            this.handleRectangleCreated
        );

        this.map.on(
            L.Draw.Event.EDITMOVE,
            this.handleRectangleEdited
        );

        this.map.on(
            L.Draw.Event.EDITRESIZE,
            this.handleRectangleEdited
        );

        this.map.on(
            L.Draw.Event.EDITVERTEX,
            this.handleRectangleEdited
        );

        this.map.on(
            L.Draw.Event.EDITED,
            this.handleRectangleEdited
        );

        this.map.on(
            L.Draw.Event.EDITSTART,
            this.handleRectangleEditStart
        );

        this.map.on(
            L.Draw.Event.EDITSTOP,
            this.handleRectangleEditStop
        );

        requestAnimationFrame(() => {
            if (!this.destroyed) {
                this.map.invalidateSize({ pan: false });
            }
        });
    }

    handleMouseMove(event) {
        this.cursorCoordinates.textContent =
            `Cursor coordinates | Latitude: ${event.latlng.lat.toFixed(5)}°` +
            ` | Longitude: ${event.latlng.lng.toFixed(5)}°`;
    }

    handleMapClick(event) {
        if (this.selectionMode !== "point") {
            return;
        }

        this.selectPoint(
            event.latlng.lat,
            event.latlng.lng
        );
    }

    handleRectangleCreated(event) {
        if (event.layerType !== "rectangle") {
            return;
        }

        this.stopEditing();
        this.drawnItems.clearLayers();

        this.marker = null;
        this.selectionLayer = event.layer;

        this.styleRectangle(this.selectionLayer);
        this.drawnItems.addLayer(this.selectionLayer);

        this.selectionMode = "region";

        this.saveRectangleSelection();
        this.updateButtons();
    }

    styleRectangle(rectangle) {
        rectangle.setStyle({
            color: "#39a7ff",
            weight: 3,
            opacity: 1,
            fill: true,
            fillColor: "#2787ed",
            fillOpacity: 0.24,
            interactive: false
        });

        rectangle.bringToFront();
    }

    syncCoordinateInputs(bounds) {
        this.minLatInput.input.value =
            bounds.getSouth().toFixed(5);

        this.maxLatInput.input.value =
            bounds.getNorth().toFixed(5);

        this.minLonInput.input.value =
            bounds.getWest().toFixed(5);

        this.maxLonInput.input.value =
            bounds.getEast().toFixed(5);
    }

    saveRectangleSelection() {
        if (!this.selectionLayer) {
            return;
        }

        const bounds = this.selectionLayer.getBounds();

        this.currentSelection = {
            type: "region",
            bounds: {
                minLatitude: bounds.getSouth(),
                maxLatitude: bounds.getNorth(),
                minLongitude: bounds.getWest(),
                maxLongitude: bounds.getEast()
            }
        };

        this.syncCoordinateInputs(bounds);

        this.fetchButton.disabled = false;
        this.editButton.disabled = false;

        this.setStatus(
            `Selected region: ${bounds.getSouth().toFixed(4)}° to ` +
            `${bounds.getNorth().toFixed(4)}° latitude; ` +
            `${bounds.getWest().toFixed(4)}° to ` +
            `${bounds.getEast().toFixed(4)}° longitude.`
        );

        this.emitSelection(this.currentSelection);
    }

    handleRectangleEdited() {
        this.saveRectangleSelection();
    }

    handleRectangleEditStart() {
        this.setStatus(
            "Resize the rectangle using its editing handles."
        );
    }

    handleRectangleEditStop() {
        this.saveRectangleSelection();
    }

    selectPoint(latitude, longitude) {
        this.stopEditing();
        this.drawnItems.clearLayers();

        this.selectionLayer = null;

        this.marker = L.marker(
            [latitude, longitude],
            { draggable: true }
        ).addTo(this.drawnItems);

        const savePoint = latlng => {
            this.currentSelection = {
                type: "point",
                latitude: latlng.lat,
                longitude: latlng.lng
            };

            this.fetchButton.disabled = false;
            this.editButton.disabled = true;

            this.setStatus(
                `Selected point: ${latlng.lat.toFixed(5)}° latitude, ` +
                `${latlng.lng.toFixed(5)}° longitude.`
            );

            this.emitSelection(this.currentSelection);
        };

        this.marker.on("dragend", event => {
            savePoint(event.target.getLatLng());
        });

        savePoint(L.latLng(latitude, longitude));
    }

    setSelectionMode(mode) {
        this.rectangleDrawer.disable();
        this.stopEditing();

        this.selectionMode = mode;

        if (mode === "region") {
            this.rectangleDrawer.enable();

            this.setStatus(
                "Drag across the map to select a rectangular region."
            );
        } else if (mode === "point") {
            this.setStatus("Click the map to select a point.");
        }

        this.updateButtons();
    }

    toggleRectangleEditing() {
        if (!this.selectionLayer) {
            this.setStatus(
                "Draw a rectangle or apply custom coordinates first."
            );
            return;
        }

        if (this.editToolbar) {
            this.stopEditing();
            this.setStatus("Rectangle editing finished.");
            return;
        }

        this.rectangleDrawer.disable();

        this.editToolbar = new L.EditToolbar.Edit(this.map, {
            featureGroup: this.drawnItems
        });

        this.editToolbar.enable();

        this.editButton.textContent = "Finish Resizing";

        this.setStatus(
            "Drag the rectangle's corner handles to resize it."
        );
    }

    stopEditing() {
        if (!this.editToolbar) {
            return;
        }

        const toolbar = this.editToolbar;
        this.editToolbar = null;

        toolbar.save();
        toolbar.disable();

        this.editButton.textContent = "Resize Rectangle";

        if (this.selectionLayer) {
            this.saveRectangleSelection();
        }
    }

    applyCustomCoordinates() {
        const south = Number(this.minLatInput.input.value);
        const north = Number(this.maxLatInput.input.value);
        const west = Number(this.minLonInput.input.value);
        const east = Number(this.maxLonInput.input.value);

        if (
            !Number.isFinite(south) ||
            !Number.isFinite(north) ||
            !Number.isFinite(west) ||
            !Number.isFinite(east) ||
            south < -90 ||
            north > 90 ||
            west < -180 ||
            east > 180 ||
            south >= north ||
            west >= east
        ) {
            this.setStatus(
                "Invalid coordinates. Check the latitude and longitude limits."
            );
            return;
        }

        this.rectangleDrawer.disable();
        this.stopEditing();
        this.drawnItems.clearLayers();

        this.marker = null;

        const bounds = L.latLngBounds(
            [south, west],
            [north, east]
        );

        this.selectionLayer = L.rectangle(bounds, {
            color: "#39a7ff",
            weight: 3,
            opacity: 1,
            fill: true,
            fillColor: "#2787ed",
            fillOpacity: 0.24,
            interactive: false
        });

        this.drawnItems.addLayer(this.selectionLayer);

        this.selectionMode = "region";

        this.saveRectangleSelection();

        this.map.fitBounds(bounds, {
            padding: [24, 24],
            maxZoom: 10
        });

        this.updateButtons();
    }

    setRegionalStatistics({ time, bounds, results }) {
        const container = this.regionalStatisticsElement;

        if (!container) {
            return;
        }

        container.replaceChildren();
        container.style.display = "block";

        const heading = document.createElement("div");

        heading.textContent = "Regional Weather Statistics";

        Object.assign(heading.style, {
            fontSize: "17px",
            fontWeight: "700",
            marginBottom: "5px"
        });

        const subtitle = document.createElement("div");

        subtitle.textContent =
            `ERA5 · ${time} · ` +
            `${bounds.minLatitude}° to ${bounds.maxLatitude}° latitude · ` +
            `${bounds.minLongitude}° to ${bounds.maxLongitude}° longitude`;

        Object.assign(subtitle.style, {
            color: "#9eacc2",
            fontSize: "11px",
            marginBottom: "16px",
            overflowWrap: "anywhere"
        });

        container.append(heading, subtitle);

        const grid = document.createElement("div");

        Object.assign(grid.style, {
            display: "grid",
            gridTemplateColumns:
                "repeat(auto-fit, minmax(260px, 1fr))",
            gap: "12px"
        });

        const createText = (tag, value, styles = {}) => {
            const element = document.createElement(tag);
            element.textContent = value;

            Object.assign(element.style, styles);

            return element;
        };

        const formatValue = value => {
            if (typeof value !== "number" || !Number.isFinite(value)) {
                return "N/A";
            }

            return value.toLocaleString(undefined, {
                maximumFractionDigits: 3
            });
        };

        for (const result of results) {
            const card = document.createElement("div");

            Object.assign(card.style, {
                padding: "14px",
                background: "#0c121e",
                border: "1px solid #293951",
                borderRadius: "7px",
                minWidth: "0"
            });

            const variableName = result.variable;
            const unit = result.unit ?? "";
            const stats = result.statistics;
            const percentiles = stats.percentiles;
            const locations = result.extrema_locations;
            const gridInfo = result.grid;

            card.appendChild(
                createText("div", variableName, {
                    fontSize: "14px",
                    fontWeight: "700",
                    marginBottom: "10px",
                    overflowWrap: "anywhere"
                })
            );

            const table = document.createElement("table");

            Object.assign(table.style, {
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "12px",
                fontVariantNumeric: "tabular-nums"
            });

            const rows = [
                ["Area-weighted mean", stats.area_weighted_mean],
                ["Minimum", stats.minimum],
                ["Maximum", stats.maximum],
                ["Standard deviation", stats.standard_deviation],
                ["P10", percentiles.p10],
                ["P25", percentiles.p25],
                ["Median (P50)", percentiles.p50],
                ["P75", percentiles.p75],
                ["P90", percentiles.p90]
            ];

            for (const [label, value] of rows) {
                const row = document.createElement("tr");

                const nameCell = createText("td", label, {
                    padding: "5px 4px",
                    color: "#9eacc2",
                    borderBottom: "1px solid #202f45"
                });

                const valueCell = createText(
                    "td",
                    `${formatValue(value)} ${unit}`.trim(),
                    {
                        padding: "5px 4px",
                        textAlign: "right",
                        color: "#e8edf7",
                        borderBottom: "1px solid #202f45",
                        overflowWrap: "anywhere"
                    }
                );

                row.append(nameCell, valueCell);
                table.appendChild(row);
            }

            card.appendChild(table);

            const minimumLocation = locations.minimum;
            const maximumLocation = locations.maximum;

            card.appendChild(
                createText(
                    "div",
                    `Minimum location: ${minimumLocation.latitude}°, ` +
                    `${minimumLocation.longitude}°`,
                    {
                        marginTop: "12px",
                        color: "#8fc8ff",
                        fontSize: "11px",
                        overflowWrap: "anywhere"
                    }
                )
            );

            card.appendChild(
                createText(
                    "div",
                    `Maximum location: ${maximumLocation.latitude}°, ` +
                    `${maximumLocation.longitude}°`,
                    {
                        marginTop: "4px",
                        color: "#ffb879",
                        fontSize: "11px",
                        overflowWrap: "anywhere"
                    }
                )
            );

            card.appendChild(
                createText(
                    "div",
                    `Valid cells: ${gridInfo.valid_cell_count} / ` +
                    `${gridInfo.total_cell_count} · ` +
                    `Missing: ${gridInfo.missing_cell_count}`,
                    {
                        marginTop: "8px",
                        color: "#9eacc2",
                        fontSize: "11px"
                    }
                )
            );

            grid.appendChild(card);
        }

        container.appendChild(grid);
    }

    async searchPlace() {
        const query = this.searchInput.value.trim();

        if (!query) {
            this.setStatus("Enter a place to search for.");
            return;
        }

        this.searchButton.disabled = true;
        this.setStatus("Searching for place...");

        try {
            const url = new URL(
                "https://nominatim.openstreetmap.org/search"
            );

            url.searchParams.set("q", query);
            url.searchParams.set("format", "jsonv2");
            url.searchParams.set("limit", "1");

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(
                    `Place search failed (${response.status}).`
                );
            }

            const results = await response.json();

            if (!results.length) {
                this.setStatus("No matching place found.");
                return;
            }

            const result = results[0];

            this.map.setView(
                [Number(result.lat), Number(result.lon)],
                9
            );

            this.setSelectionMode("point");

            this.selectPoint(
                Number(result.lat),
                Number(result.lon)
            );
        } catch (error) {
            console.error("[Geographic Selection]", error);
            this.setStatus(`Search failed: ${error.message}`);
        } finally {
            this.searchButton.disabled = false;
        }
    }

    fetchSelectedData() {
        if (!this.currentSelection) {
            this.setStatus(
                "Select a point or define a rectangle first."
            );
            return;
        }

        const selection = {
            ...this.currentSelection,
            ...(this.currentSelection.bounds
                ? {
                    bounds: {
                        ...this.currentSelection.bounds
                    }
                }
                : {})
        };

        console.log(
            "[Avani] Fetch Data requested:",
            selection
        );

        if (typeof this.onFetchData === "function") {
            this.onFetchData(selection);
        } else {
            this.setStatus(
                "Historical data fetching is not connected."
            );
        }
    }

    clearSelection() {
        this.rectangleDrawer.disable();
        this.stopEditing();
        this.drawnItems.clearLayers();

        this.marker = null;
        this.selectionLayer = null;
        this.currentSelection = null;

        this.fetchButton.disabled = true;
        this.editButton.disabled = true;

        this.selectionMode = "point";

        this.updateButtons();

        this.setStatus("Selection cleared.");
        this.emitSelection(null);
    }

    emitSelection(selection) {
        if (typeof this.onSelectionChange === "function") {
            this.onSelectionChange(selection);
        }
    }

    updateButtons() {
        this.pointButton.style.background =
            this.selectionMode === "point"
                ? "#3679d8"
                : "#202f45";

        this.regionButton.style.background =
            this.selectionMode === "region"
                ? "#3679d8"
                : "#202f45";
    }

    setStatus(message) {
        this.statusText.textContent = message;
    }

    makeLabel(text) {
        const label = document.createElement("div");
        label.textContent = text;

        Object.assign(label.style, {
            margin: "12px 0 6px",
            color: "#9eacc2",
            fontSize: "10px",
            fontWeight: "700",
            letterSpacing: "0.8px"
        });

        return label;
    }

    makeRow() {
        const row = document.createElement("div");

        Object.assign(row.style, {
            display: "flex",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "8px",
            marginBottom: "12px"
        });

        return row;
    }

    makeButton(text, background) {
        const button = document.createElement("button");

        button.type = "button";
        button.textContent = text;

        Object.assign(button.style, this.buttonStyle(), {
            background,
            flex: "0 0 auto"
        });

        return button;
    }

    makeNumberInput(labelText, min, max, value) {
        const wrapper = document.createElement("label");

        Object.assign(wrapper.style, {
            display: "flex",
            flexDirection: "column",
            gap: "5px",
            color: "#cbd5e4",
            fontSize: "12px"
        });

        const label = document.createElement("span");
        label.textContent = labelText;

        const input = document.createElement("input");

        input.type = "number";
        input.min = String(min);
        input.max = String(max);
        input.step = "any";
        input.value = String(value);

        Object.assign(input.style, this.controlStyle(), {
            width: "100%"
        });

        wrapper.append(label, input);

        return { wrapper, input };
    }

    controlStyle() {
        return {
            boxSizing: "border-box",
            padding: "10px 12px",
            background: "#111c2b",
            color: "#e8edf7",
            border: "1px solid #40506a",
            borderRadius: "6px",
            outline: "none",
            font: "inherit"
        };
    }

    buttonStyle() {
        return {
            boxSizing: "border-box",
            padding: "9px 12px",
            background: "#202f45",
            color: "#e8edf7",
            border: "1px solid #40506a",
            borderRadius: "6px",
            font: "inherit",
            cursor: "pointer"
        };
    }

    destroy() {
        this.destroyed = true;

        this.rectangleDrawer?.disable();
        this.stopEditing();

        this.map.off("click", this.handleMapClick);
        this.map.off("mousemove", this.handleMouseMove);

        this.map.off(
            L.Draw.Event.CREATED,
            this.handleRectangleCreated
        );

        this.map.off(
            L.Draw.Event.EDITMOVE,
            this.handleRectangleEdited
        );

        this.map.off(
            L.Draw.Event.EDITRESIZE,
            this.handleRectangleEdited
        );

        this.map.off(
            L.Draw.Event.EDITVERTEX,
            this.handleRectangleEdited
        );

        this.map.off(
            L.Draw.Event.EDITED,
            this.handleRectangleEdited
        );

        this.map.off(
            L.Draw.Event.EDITSTART,
            this.handleRectangleEditStart
        );

        this.map.off(
            L.Draw.Event.EDITSTOP,
            this.handleRectangleEditStop
        );

        this.map.removeLayer(this.drawnItems);
        this.element.remove();
    }
}
