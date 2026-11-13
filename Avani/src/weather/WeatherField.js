export class WeatherField
{
    constructor(observations = [])
    {
        this.observations = observations;

        this.forecastRun = null;

        this.validTimes = new Map();
    }

    addObservation(observation)
    {
        if (this.forecastRun === null)
        {
            this.forecastRun =
                observation.forecastRun;
        }

        if (!this.validTimes.has(observation.validTime))
        {
            this.validTimes.set(
                observation.validTime,
                new Map()
            );
        }

        const ensembleMembers =
            this.validTimes.get(
                observation.validTime
            );

        if (!ensembleMembers.has(observation.ensembleMember))
        {
            ensembleMembers.set(
                observation.ensembleMember,
                []
            );
        }

        ensembleMembers
            .get(observation.ensembleMember)
            .push(observation);

        this.observations.push(observation);
    }

    addObservations(observations)
    {
        for (const observation of observations)
        {
            this.addObservation(observation);
        }
    }

    getObservations()
    {
        return this.observations;
    }

    getValidTimes()
    {
        return this.validTimes.keys();
    }

    getEnsembleMembers(validTime)
    {
        const ensembleMembers =
            this.validTimes.get(validTime);

        if (!ensembleMembers)
        {
            return [];
        }

        return ensembleMembers.keys();
    }

    getObservationsAt(
        validTime,
        ensembleMember
    )
    {
        const ensembleMembers =
            this.validTimes.get(validTime);

        if (!ensembleMembers)
        {
            return [];
        }

        return (
            ensembleMembers.get(ensembleMember)
            ?? []
        );
    }

    getField(
        validTime,
        ensembleMember
    )
    {
        return this.getObservationsAt(
            validTime,
            ensembleMember
        );
    }
}