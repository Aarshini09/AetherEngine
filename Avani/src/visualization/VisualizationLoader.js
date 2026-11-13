import { VisualizationData } from "./VisualizationData.js";

export class VisualizationLoader {

    async load(url) {
        const response =
            await fetch(url);

        if (!response.ok) {
            throw new Error(
                `Failed to load visualization data: ${response.status} ${response.statusText}`
            );
        }

        const data =
            await response.json();

        return new VisualizationData(
            data
        );
    }
}