export class WeatherStatistics
{
    static calculateMean(
        observations,
        property
    )
    {
        let sum = 0;
        let count = 0;

        for (const observation of observations)
        {
            const value =
                observation[property];

            if (value === null || value === undefined)
            {
                continue;
            }

            sum += value;
            count++;
        }

        if (count === 0)
        {
            return null;
        }

        return sum / count;
    }

    static calculateMinimum(
        observations,
        property
    )
    {
        let minimum = Infinity;

        for (const observation of observations)
        {
            const value =
                observation[property];

            if (value === null || value === undefined)
            {
                continue;
            }

            minimum =
                Math.min(
                    minimum,
                    value
                );
        }

        if (minimum === Infinity)
        {
            return null;
        }

        return minimum;
    }

    static calculateMaximum(
        observations,
        property
    )
    {
        let maximum = -Infinity;

        for (const observation of observations)
        {
            const value =
                observation[property];

            if (value === null || value === undefined)
            {
                continue;
            }

            maximum =
                Math.max(
                    maximum,
                    value
                );
        }

        if (maximum === -Infinity)
        {
            return null;
        }

        return maximum;
    }

    static calculate(
        observations,
        property
    )
    {
        return {
            minimum:
                this.calculateMinimum(
                    observations,
                    property
                ),

            maximum:
                this.calculateMaximum(
                    observations,
                    property
                ),

            mean:
                this.calculateMean(
                    observations,
                    property
                )
        };
    }
}