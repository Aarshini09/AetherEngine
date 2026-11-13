export class AnomalyCalculator
{
    static calculate(
        observation,
        baseline,
        property
    )
    {
        const value =
            observation[property];

        if (
            value === null ||
            value === undefined
        )
        {
            return null;
        }

        if (
            baseline === null ||
            baseline === undefined
        )
        {
            return null;
        }

        return value - baseline;
    }
}