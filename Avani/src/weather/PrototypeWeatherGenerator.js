export class PrototypeWeatherGenerator
{
    constructor({
        longitudeStep = 5,
        latitudeStep = 5,
        validTimes = [],
        ensembleMembers = [0]
    } = {})
    {
        this.longitudeStep = longitudeStep;
        this.latitudeStep = latitudeStep;

        this.validTimes = validTimes;
        this.ensembleMembers = ensembleMembers;
    }

    generate()
    {
        const observations = [];

        for (
            let timeIndex = 0;
            timeIndex < this.validTimes.length;
            timeIndex++
        )
        {
            const validTime =
                this.validTimes[timeIndex];

            for (
                const ensembleMember of this.ensembleMembers
            )
            {
                for (
                    let latitude = -90;
                    latitude <= 90;
                    latitude += this.latitudeStep
                )
                {
                    for (
                        let longitude = -180;
                        longitude < 180;
                        longitude += this.longitudeStep
                    )
                    {
                        const temperature =
                            this.generateTemperature(
                                longitude,
                                latitude,
                                validTime,
                                timeIndex
                            );

                        const pressure =
                            this.generatePressure(
                                longitude,
                                latitude
                            );

                        const windSpeed =
                            this.generateWindSpeed(
                                longitude,
                                latitude
                            );

                        observations.push({
                            longitude,
                            latitude,
                            height: 0,

                            validTime,
                            ensembleMember,

                            temperature,
                            pressure,
                            windSpeed,

                            windDirection: 0,
                            rainfall: 0
                        });
                    }
                }
            }
        }

        return observations;
    }

    generateTemperature(
        longitude,
        latitude,
        validTime,
        timeIndex
    )
    {
        const latitudeEffect =
            30 *
            Math.cos(
                latitude *
                Math.PI /
                180
            );

        const baseTemperature =
            10 +
            latitudeEffect;

        const longitudeEffect =
            3 *
            Math.sin(
                longitude *
                Math.PI /
                180
            );

        const anomaly =
            this.generateTemperatureAnomaly(
                longitude,
                latitude,
                timeIndex
            );

        return (
            baseTemperature +
            longitudeEffect +
            anomaly
        );
    }

    generateTemperatureAnomaly(
        longitude,
        latitude,
        timeIndex
    )
    {
        /*
         * Moving synthetic heat anomaly.
         *
         * The anomaly moves eastward
         * with each forecast time.
         */

        const centerLongitude =
            60 + timeIndex * 10;

        const centerLatitude =
            20;

        const longitudeDistance =
            this.longitudeDistance(
                longitude,
                centerLongitude
            );

        const latitudeDistance =
            latitude -
            centerLatitude;

        const distanceSquared =
            longitudeDistance *
            longitudeDistance +
            latitudeDistance *
            latitudeDistance;

        const spread = 15;

        const strength = 8;

        return (
            strength *
            Math.exp(
                -distanceSquared /
                (
                    2 *
                    spread *
                    spread
                )
            )
        );
    }

    longitudeDistance(
        longitudeA,
        longitudeB
    )
    {
        let distance =
            longitudeA -
            longitudeB;

        if (distance > 180)
        {
            distance -= 360;
        }

        if (distance < -180)
        {
            distance += 360;
        }

        return distance;
    }

    generatePressure(
        longitude,
        latitude
    )
    {
        return (
            1013 -
            8 *
            Math.sin(
                latitude *
                Math.PI /
                180
            )
        );
    }

    generateWindSpeed(
        longitude,
        latitude
    )
    {
        return (
            5 +
            3 *
            Math.abs(
                Math.sin(
                    latitude *
                    Math.PI /
                    180
                )
            )
        );
    }
}