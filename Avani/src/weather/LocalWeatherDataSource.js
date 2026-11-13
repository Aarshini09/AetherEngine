import { WeatherDataSource } from "./WeatherDataSource.js";
import { WeatherObservation } from "./WeatherObservation.js";

export class LocalWeatherDataSource extends WeatherDataSource
{
    constructor(url)
    {
        super();

        this.url = url;
        this.observations = [];
    }

    async load()
    {
        const response = await fetch(this.url);

        if (!response.ok)
        {
            throw new Error(
                `Failed to load weather data: ${response.status}`
            );
        }

        const data = await response.json();

        this.observations = data.observations.map(
            observation =>
                new WeatherObservation({
                    ...observation,
                    forecastRun: data.forecastRun
                })
        );

        return this.observations;
    }

    getObservations()
    {
        return this.observations;
    }
}