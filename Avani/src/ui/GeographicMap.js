import L from "leaflet";
import "leaflet/dist/leaflet.css";

export class GeographicMap {
    constructor() {
        this.element = document.createElement("section");

        Object.assign(this.element.style, {
            width: "100%",
            maxWidth: "1600px",
            height: "380px",
            margin: "24px auto",
            padding: "0 16px",
            boxSizing: "border-box"
        });

        this.mapElement = document.createElement("div");

        Object.assign(this.mapElement.style, {
            width: "100%",
            height: "100%",
            background: "#101722",
            border: "1px solid #344157",
            borderRadius: "8px",
            overflow: "hidden"
        });

        this.element.appendChild(this.mapElement);

        this.map = L.map(this.mapElement).setView(
            [20.5937, 78.9629],
            4
        );

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19,
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }
        ).addTo(this.map);

        requestAnimationFrame(() => {
            this.map.invalidateSize();
        });
    }
}
