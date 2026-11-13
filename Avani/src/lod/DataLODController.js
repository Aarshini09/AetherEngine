
export class DataLODController {
    constructor({
        initialDistance,
        distancePerLevel = 2,
        maxPositiveLevel = 8,
        maxNegativeLevel = 8,
        initialPointBudget = 10_000,
        intermediatePointBudget = 50_000,
        maxPointBudget = 500_000,
        maxSourceRows = 721,
        maxSourceColumns = 1440
    } = {}) {
        if (!Number.isFinite(initialDistance) || initialDistance <= 0) {
            throw new Error("A valid initialDistance is required.");
        }

        if (!Number.isFinite(distancePerLevel) || distancePerLevel <= 0) {
            throw new Error("distancePerLevel must be positive.");
        }

        if (
            !Number.isInteger(maxPositiveLevel) || maxPositiveLevel < 0 ||
            !Number.isInteger(maxNegativeLevel) || maxNegativeLevel < 0
        ) {
            throw new Error("LOD levels must be non-negative integers.");
        }

        if (
            !Number.isInteger(initialPointBudget) ||
            !Number.isInteger(intermediatePointBudget) ||
            !Number.isInteger(maxPointBudget) ||
            initialPointBudget < 4 ||
            initialPointBudget > intermediatePointBudget ||
            intermediatePointBudget > maxPointBudget
        ) {
            throw new Error("Invalid point budgets.");
        }

        this.initialDistance = initialDistance;
        this.distancePerLevel = distancePerLevel;
        this.maxPositiveLevel = maxPositiveLevel;
        this.maxNegativeLevel = maxNegativeLevel;

        this.initialPointBudget = initialPointBudget;
        this.intermediatePointBudget = intermediatePointBudget;
        this.maxPointBudget = maxPointBudget;

        this.maxSourceRows = maxSourceRows;
        this.maxSourceColumns = maxSourceColumns;

        this.currentLevel = null;
    }

    calculateLevel(distance) {
        if (!Number.isFinite(distance) || distance <= 0) {
            throw new Error("Camera distance must be positive.");
        }

        const rawLevel =
            Math.log2(this.initialDistance / distance) *
            this.distancePerLevel;

        return Math.max(
            -this.maxNegativeLevel,
            Math.min(
                this.maxPositiveLevel,
                Math.round(rawLevel)
            )
        );
    }

    calculatePointBudget(dataLevel) {
        if (dataLevel <= 0 || this.maxPositiveLevel === 0) {
            return this.initialPointBudget;
        }

        const middleLevel = Math.min(2, this.maxPositiveLevel);

        if (dataLevel <= middleLevel) {
            const t = dataLevel / middleLevel;

            return Math.round(
                this.initialPointBudget *
                Math.pow(
                    this.intermediatePointBudget /
                        this.initialPointBudget,
                    t
                )
            );
        }

        const remainingLevels = this.maxPositiveLevel - middleLevel;

        if (remainingLevels === 0) {
            return this.maxPointBudget;
        }

        const t = Math.min(
            1,
            (dataLevel - middleLevel) / remainingLevels
        );

        return Math.min(
            this.maxPointBudget,
            Math.round(
                this.intermediatePointBudget *
                Math.pow(
                    this.maxPointBudget /
                        this.intermediatePointBudget,
                    t
                )
            )
        );
    }

    calculateGridDimensions(pointBudget) {
        // Preserve the global ERA5 grid's approximate 1:2
        // latitude-row to longitude-column proportion.
        const aspectRatio = 2;

        let rows = Math.floor(
            Math.sqrt(pointBudget / aspectRatio)
        );

        rows = Math.max(2, Math.min(rows, this.maxSourceRows));

        let columns = Math.floor(
            pointBudget / rows
        );

        columns = Math.max(
            2,
            Math.min(columns, this.maxSourceColumns)
        );

        // If source limits or rounding affect the budget,
        // reduce columns until the cap is satisfied.
        if (rows * columns > pointBudget) {
            columns = Math.floor(pointBudget / rows);
        }

        return {
            maxRows: rows,
            maxColumns: columns,
            estimatedPoints: rows * columns
        };
    }

    update(distance, visibleRegion = null) {
        const geometricLevel = this.calculateLevel(distance);
        const dataLevel = Math.max(0, geometricLevel);

        const changed = this.currentLevel !== geometricLevel;
        this.currentLevel = geometricLevel;

        const pointBudget = this.calculatePointBudget(dataLevel);

        const grid = this.calculateGridDimensions(pointBudget);

        return {
            changed,
            geometricLevel,
            dataLevel,
            pointBudget,

            maxRows: grid.maxRows,
            maxColumns: grid.maxColumns,
            estimatedPoints: grid.estimatedPoints,

            cameraDistance: distance,
            initialDistance: this.initialDistance,
            visibleRegion
        };
    }

    createRequestPlan(lodState, {
        variable = "temperature",
        time
    } = {}) {
        if (!lodState || !lodState.visibleRegion?.visible) {
            return null;
        }

        if (!time) {
            throw new Error("A time is required for a data request.");
        }

        const region = lodState.visibleRegion;

        return {
            variable,
            time,

            minLatitude: region.minLatitude,
            maxLatitude: region.maxLatitude,
            minLongitude: region.minLongitude,
            maxLongitude: region.maxLongitude,

            maxRows: lodState.maxRows,
            maxColumns: lodState.maxColumns,
            pointBudget: lodState.pointBudget,

            geometricLevel: lodState.geometricLevel,
            dataLevel: lodState.dataLevel
        };
    }

    getRegionKey(region) {
        if (!region?.visible) {
            return null;
        }

        return [
            region.minLatitude.toFixed(2),
            region.maxLatitude.toFixed(2),
            region.minLongitude.toFixed(2),
            region.maxLongitude.toFixed(2),
            Boolean(region.crossesAntimeridian)
        ].join(":");
    }

    getCurrentLevel() {
        return this.currentLevel;
    }
}
