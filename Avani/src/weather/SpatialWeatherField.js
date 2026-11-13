import {
    geoToCartesian
} from "../gis/CoordinateConversion.js";

export class SpatialWeatherField
{
    constructor(earth)
    {
        this.earth = earth;

        this.observations = [];

        // cellId -> observations
        this.cells = new Map();
    }

    addObservation(
        observation,
        cell
    )
    {
        this.observations.push(
            observation
        );

        if (!this.cells.has(cell.id))
        {
            this.cells.set(
                cell.id,
                []
            );
        }

        this.cells
            .get(cell.id)
            .push(observation);
    }

    addObservations(
        observations,
        icosahedron
    )
    {
        for (const observation of observations)
        {
            const position =
                geoToCartesian(
                    observation,
                    this.earth.radius
                );

            const cell =
                icosahedron.findCell(
                    position
                );

            if (!cell)
            {
                continue;
            }

            this.addObservation(
                observation,
                cell
            );
        }
    }

    getObservations()
    {
        return this.observations;
    }

    getCellObservations(cellId)
    {
        return (
            this.cells.get(cellId)
            ?? []
        );
    }

    getCellIds()
    {
        return this.cells.keys();
    }

    hasCell(cellId)
    {
        return this.cells.has(cellId);
    }

    getCellCount()
    {
        return this.cells.size;
    }

    getObservationCount()
    {
        return this.observations.length;
    }
}