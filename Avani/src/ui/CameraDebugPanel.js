export class CameraDebugPanel {
    constructor(parent = document.body) {
        this.container = document.createElement("div");

        Object.assign(this.container.style, {
            position: "absolute",
            top: "20px",
            left: "270px",
            width: "270px",
            maxHeight: "calc(100% - 40px)",
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

        // Style navigation inputs consistently.
        this.container.querySelectorAll("input").forEach(input => {
            Object.assign(input.style, {
                width: "120px",
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

        // Style the navigation button.
        Object.assign(this.goToButton.style, {
            display: "block",
            width: "100%",
            boxSizing: "border-box",
            padding: "8px",
            cursor: "pointer",
            background: "#1b1b1b",
            color: "#f1f1f1",
            border: "1px solid #555",
            borderRadius: "4px",
            fontFamily: "monospace",
            fontSize: "12px"
        });

        this.goToButton.addEventListener("mouseenter", () => {
            this.goToButton.style.background = "#303030";
        });

        this.goToButton.addEventListener("mouseleave", () => {
            this.goToButton.style.background = "#1b1b1b";
        });
    }

    createUI() {
        this.container.innerHTML = `
            <div style="
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 14px;
            ">
                AVANI CAMERA DEBUG
            </div>

            <div style="
                margin-bottom: 8px;
                opacity: 0.8;
            ">
                CAMERA POSITION
            </div>

            <div style="margin-bottom: 4px;">
                X: <span id="camera-x">0</span>
            </div>

            <div style="margin-bottom: 4px;">
                Y: <span id="camera-y">0</span>
            </div>

            <div style="margin-bottom: 4px;">
                Z: <span id="camera-z">0</span>
            </div>

            <div style="margin-top: 6px;">
                Distance: <span id="camera-distance">0</span>
            </div>

            <hr style="
                margin: 15px 0;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.2);
            ">

            <div style="
                margin-bottom: 8px;
                opacity: 0.8;
            ">
                LOOKING AT
            </div>

            <div style="margin-bottom: 4px;">
                Longitude:
                <span id="camera-longitude">---</span>°
            </div>

            <div style="margin-bottom: 4px;">
                Latitude:
                <span id="camera-latitude">---</span>°
            </div>

            <div>
                Height:
                <span id="camera-height">---</span>
            </div>

            <hr style="
                margin: 15px 0;
                border: none;
                border-top: 1px solid rgba(255,255,255,0.2);
            ">

            <div style="
                margin-bottom: 10px;
                opacity: 0.8;
            ">
                NAVIGATE TO
            </div>

            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 8px;
            ">
                <label for="camera-target-longitude">
                    Longitude
                </label>

                <input
                    id="camera-target-longitude"
                    type="number"
                    value="0"
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
                <label for="camera-target-latitude">
                    Latitude
                </label>

                <input
                    id="camera-target-latitude"
                    type="number"
                    value="0"
                    step="0.0001"
                >
            </div>

            <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin-bottom: 10px;
            ">
                <label for="camera-target-height">
                    Height
                </label>

                <input
                    id="camera-target-height"
                    type="number"
                    value="0"
                    step="0.01"
                >
            </div>

            <button id="camera-go-to">
                GO TO LOCATION
            </button>

            <div style="
                margin-top: 14px;
                font-size: 11px;
                opacity: 0.6;
                line-height: 1.7;
            ">
                Mouse drag → Orbit<br>
                ← → → Longitude<br>
                ↑ ↓ → North / South<br>
                Ctrl + → Zoom In<br>
                Ctrl - → Zoom Out
            </div>
        `;

        // Camera position outputs.
        this.x = this.container.querySelector("#camera-x");
        this.y = this.container.querySelector("#camera-y");
        this.z = this.container.querySelector("#camera-z");
        this.distance = this.container.querySelector("#camera-distance");

        // Looking-at coordinate outputs.
        this.longitude = this.container.querySelector("#camera-longitude");
        this.latitude = this.container.querySelector("#camera-latitude");
        this.height = this.container.querySelector("#camera-height");

        // Navigation inputs.
        this.targetLongitude =
            this.container.querySelector("#camera-target-longitude");

        this.targetLatitude =
            this.container.querySelector("#camera-target-latitude");

        this.targetHeight =
            this.container.querySelector("#camera-target-height");

        this.goToButton =
            this.container.querySelector("#camera-go-to");
    }

    getTargetCoordinate() {
        return {
            longitude: Number(this.targetLongitude.value),
            latitude: Number(this.targetLatitude.value),
            height: Number(this.targetHeight.value)
        };
    }

    update(camera, coordinate) {
        const position = camera.camera.position;

        this.x.textContent = position.x.toFixed(4);
        this.y.textContent = position.y.toFixed(4);
        this.z.textContent = position.z.toFixed(4);
        this.distance.textContent = position.length().toFixed(4);

        if (coordinate === null) {
            this.longitude.textContent = "---";
            this.latitude.textContent = "---";
            this.height.textContent = "---";
            return;
        }

        this.longitude.textContent =
            coordinate.longitude.toFixed(4);

        this.latitude.textContent =
            coordinate.latitude.toFixed(4);

        this.height.textContent =
            coordinate.height.toFixed(4);
    }
}