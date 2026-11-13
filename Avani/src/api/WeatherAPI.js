
const API_BASE_URL = "http://127.0.0.1:8000/api";

export class WeatherAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl.replace(/\/+$/, "");
    }

    async request(path, params = {}) {
        const url = new URL(
            `${this.baseUrl}${path}`
        );

        for (const [key, value] of Object.entries(params)) {
            if (value !== undefined && value !== null) {
                url.searchParams.set(key, String(value));
            }
        }

        const response = await fetch(url);

        if (!response.ok) {
            const detail = await response.text();

            throw new Error(
                `Avani API error (${response.status}): ${detail}`
            );
        }

        return response.json();
    }

    async getHealth() {
        return this.request("/health");
    }

    async getMetadata() {
    return this.request("/weather/metadata");
}

    async getTimeSeries({
        variable = "temperature",
        startTime,
        endTime,
        latitude,
        longitude,
        timeStep = 1
    }) {
        if (!startTime || !endTime) {
            throw new Error(
                "Both startTime and endTime are required."
            );
        }

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude)
        ) {
            throw new Error(
                "Valid latitude and longitude are required."
            );
        }

        if (!Number.isInteger(timeStep) || timeStep < 1) {
            throw new Error(
                "timeStep must be a positive integer."
            );
        }

        return this.request("/weather/time-series", {
            variable,
            start_time: startTime,
            end_time: endTime,
            latitude,
            longitude,
            time_step: timeStep
        });
    }
    
    async getWeatherFrame({
        variable = "temperature",
        time,
        minLatitude = -90,
        maxLatitude = 90,
        minLongitude = -180,
        maxLongitude = 180,
        maxRows = 181,
        maxColumns = 360
    }) {
        if (!time) {
            throw new Error("A frame time is required.");
        }

        return this.request("/weather/frame", {
            variable,
            time,
            min_latitude: minLatitude,
            max_latitude: maxLatitude,
            min_longitude: minLongitude,
            max_longitude: maxLongitude,
            max_rows: maxRows,
            max_columns: maxColumns
        });
    }
    
    async getRegionStatistics({
        variable = "temperature",
        time,
        minLatitude,
        maxLatitude,
        minLongitude,
        maxLongitude
    }) {
        if (!time) {
            throw new Error("A timestamp is required for regional statistics.");
        }

        return this.request("/weather/region-statistics", {
            variable,
            time,
            min_latitude: minLatitude,
            max_latitude: maxLatitude,
            min_longitude: minLongitude,
            max_longitude: maxLongitude
        });
    }


    async postRequest(path, body) {
        const response = await fetch(
            `${this.baseUrl}${path}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(body)
            }
        );

        if (!response.ok) {
            const detail = await response.text();

            throw new Error(
                `Avani API error (${response.status}): ${detail}`
            );
        }

        return response.json();
    }

    async runAnomalyAnalysis({
        variable = "temperature",
        minLatitude,
        maxLatitude,
        minLongitude,
        maxLongitude,
        startTime,
        endTime,
        intervalHours = 6
    }) {
        if (!startTime || !endTime) {
            throw new Error(
                "Analysis startTime and endTime are required."
            );
        }

        if (
            minLatitude >= maxLatitude ||
            minLongitude >= maxLongitude
        ) {
            throw new Error(
                "Invalid analysis geographic bounds."
            );
        }

        if (
            !Number.isInteger(intervalHours) ||
            intervalHours < 1
        ) {
            throw new Error(
                "intervalHours must be a positive integer."
            );
        }

        return this.postRequest("/analysis/run", {
            variable,
            min_latitude: minLatitude,
            max_latitude: maxLatitude,
            min_longitude: minLongitude,
            max_longitude: maxLongitude,
            start_time: startTime,
            end_time: endTime,
            interval_hours: intervalHours
        });
    }


async post(path, body) {
    const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        try {
            const error = await response.json();
            message = error.detail ?? message;
        } catch {
            // Keep the HTTP error message if the body isn't JSON.
        }

        throw new Error(
            typeof message === "string"
                ? message
                : JSON.stringify(message)
        );
    }

    return response.json();
}

async runScientificAnalysis(configuration) {
    return this.post(
        "/analysis/run",
        configuration
    );
}

}
