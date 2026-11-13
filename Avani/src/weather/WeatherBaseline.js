export class WeatherBaseline
{
    constructor()
    {
        this.values = new Map();
    }

    set(
        locationKey,
        property,
        value
    )
    {
        if (!this.values.has(locationKey))
        {
            this.values.set(
                locationKey,
                new Map()
            );
        }

        this.values
            .get(locationKey)
            .set(
                property,
                value
            );
    }

    get(
        locationKey,
        property
    )
    {
        const location =
            this.values.get(
                locationKey
            );

        if (!location)
        {
            return null;
        }

        return (
            location.get(property)
            ?? null
        );
    }
}