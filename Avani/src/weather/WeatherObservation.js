export class WeatherObservation
{
    constructor({
        longitude,
        latitude,
        height = 0,

        forecastRun,
        validTime,
        ensembleMember = 0,

        temperature = null,
        pressure = null,
        windSpeed = null,
        windDirection = null,
        rainfall = null
    })
    {
        // Geographic location
        this.longitude = longitude;
        this.latitude = latitude;
        this.height = height;

        // Forecast information
        this.forecastRun = forecastRun;
        this.validTime = validTime;
        this.ensembleMember = ensembleMember;

        // Weather variables
        this.temperature = temperature;
        this.pressure = pressure;
        this.windSpeed = windSpeed;
        this.windDirection = windDirection;
        this.rainfall = rainfall;

        // Spatial representation
        this.spatialCell  = null;
    }
}