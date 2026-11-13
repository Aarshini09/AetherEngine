export class DebugPanel {
    constructor(parent = document.body) {
        this.container = document.createElement("div");

        Object.assign(this.container.style, {
            position: "absolute",
            top: "50px",
            left: "20px",
            width: "240px",
            maxHeight: "calc(100% - 70px)",
            overflowY: "auto",
            overflowX: "hidden",
            boxSizing: "border-box",
            padding: "16px",
            background: "rgba(0, 0, 0, 0.88)",
            border: "1px solid rgba(255, 255, 255, 0.22)",
            borderRadius: "8px",
            color: "#f1f1f1",
            fontFamily: "monospace",
            fontSize: "13px",
            zIndex: "100",
            scrollbarWidth: "thin",
            scrollbarColor: "#555 #111"
        });

        parent.appendChild(this.container);

        this.createUI();
    }

    createUI() {
        this.container.innerHTML = `
            <div style="
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 14px;
            ">
                AVANI GIS DEBUG
            </div>

            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 8px;
            ">
                <label for="debug-longitude">Longitude</label>
                <input
                    id="debug-longitude"
                    type="number"
                    value="78.9629"
                    step="0.0001"
                >
            </div>

            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 8px;
            ">
                <label for="debug-latitude">Latitude</label>
                <input
                    id="debug-latitude"
                    type="number"
                    value="20.5937"
                    step="0.0001"
                >
            </div>

            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 8px;
            ">
                <label for="debug-height">Height</label>
                <input
                    id="debug-height"
                    type="number"
                    value="0"
                    step="0.01"
                >
            </div>

            <hr style="
                margin: 15px 0;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.2);
            ">

            <div style="
                margin-bottom: 6px;
                font-weight: bold;
            ">
                CARTESIAN
            </div>

            <div style="margin-bottom: 4px;">
                X: <span id="debug-x">0</span>
            </div>

            <div style="margin-bottom: 4px;">
                Y: <span id="debug-y">0</span>
            </div>

            <div>
                Z: <span id="debug-z">0</span>
            </div>

            <hr style="
                margin: 15px 0;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.2);
            ">

            <div>
                Radius: <span id="debug-radius">0</span>
            </div>
        `;

        // Style all input fields consistently.
        this.container.querySelectorAll("input").forEach(input => {
            Object.assign(input.style, {
                width: "112px",
                minWidth: "0",
                height: "30px",
                boxSizing: "border-box",
                padding: "4px 6px",
                background: "#111",
                color: "#f1f1f1",
                border: "1px solid #444",
                borderRadius: "3px",
                fontFamily: "monospace",
                fontSize: "13px"
            });
        });

        this.longitudeInput =
            this.container.querySelector("#debug-longitude");

        this.latitudeInput =
            this.container.querySelector("#debug-latitude");

        this.heightInput =
            this.container.querySelector("#debug-height");

        this.xOutput =
            this.container.querySelector("#debug-x");

        this.yOutput =
            this.container.querySelector("#debug-y");

        this.zOutput =
            this.container.querySelector("#debug-z");

        this.radiusOutput =
            this.container.querySelector("#debug-radius");
    }

    getCoordinate() {
        return {
            longitude: Number(this.longitudeInput.value),
            latitude: Number(this.latitudeInput.value),
            height: Number(this.heightInput.value)
        };
    }

    update(coordinate, position) {
        this.xOutput.textContent = position.x.toFixed(6);
        this.yOutput.textContent = position.y.toFixed(6);
        this.zOutput.textContent = position.z.toFixed(6);
        this.radiusOutput.textContent = position.length().toFixed(6);
    }
}