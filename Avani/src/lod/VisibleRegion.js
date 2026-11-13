
import * as THREE from "three";

import {
    cartesianToGeo,
    raySphereIntersection
} from "../gis/CoordinateConversion.js";

export class VisibleRegion
{
    constructor({
        sphereRadius = 1.0,
        samplesX = 24,
        samplesY = 24,
        paddingDegrees = 1.0
    } = {})
    {
        this.sphereRadius = sphereRadius;

        this.samplesX = samplesX;
        this.samplesY = samplesY;

        this.paddingDegrees = paddingDegrees;

        this.raycaster = new THREE.Raycaster();
        this.ndc = new THREE.Vector2();
    }

    calculate(camera)
    {
        camera.updateMatrixWorld(true);

        const points = [];

        for (let y = 0; y <= this.samplesY; y++)
        {
            for (let x = 0; x <= this.samplesX; x++)
            {
                const ndcX =
                    (x / this.samplesX) * 2.0 - 1.0;

                const ndcY =
                    1.0 - (y / this.samplesY) * 2.0;

                this.ndc.set(ndcX, ndcY);

                this.raycaster.setFromCamera(
                    this.ndc,
                    camera
                );

                const position = raySphereIntersection(
                    this.raycaster.ray.origin,
                    this.raycaster.ray.direction,
                    this.sphereRadius
                );

                if (position === null)
                {
                    continue;
                }

                const coordinate = cartesianToGeo(
                    position,
                    this.sphereRadius
                );

                points.push({
                    latitude: coordinate.latitude,
                    longitude: coordinate.longitude
                });
            }
        }

        if (points.length === 0)
        {
            return {
                visible: false,
                reason: "No sphere intersection in the viewport."
            };
        }

        const latitudes = points.map(
            point => point.latitude
        );

        const longitudes = points.map(
            point => THREE.MathUtils.euclideanModulo(
                point.longitude + 180.0,
                360.0
            )
        );

        // Find the smallest longitude interval that
        // contains all sampled points, including across
        // the antimeridian.
        longitudes.sort((a, b) => a - b);

        let largestGap = -1.0;
        let largestGapIndex = 0;

        for (let i = 0; i < longitudes.length; i++)
        {
            const current = longitudes[i];

            const next =
                i + 1 < longitudes.length
                    ? longitudes[i + 1]
                    : longitudes[0] + 360.0;

            const gap = next - current;

            if (gap > largestGap)
            {
                largestGap = gap;
                largestGapIndex = i;
            }
        }

        const startIndex =
            (largestGapIndex + 1) % longitudes.length;

        const longitudeStart =
            longitudes[startIndex];

        const longitudeSpan =
            360.0 - largestGap;

        const normalizeLongitude = longitude =>
        {
            return THREE.MathUtils.euclideanModulo(
                longitude + 180.0,
                360.0
            ) - 180.0;
        };

        const minLatitude = Math.max(
            -90.0,
            Math.min(...latitudes) - this.paddingDegrees
        );

        const maxLatitude = Math.min(
            90.0,
            Math.max(...latitudes) + this.paddingDegrees
        );

        const minLongitude = normalizeLongitude(
            longitudeStart - this.paddingDegrees
        );

        const maxLongitude = normalizeLongitude(
            longitudeStart +
            longitudeSpan +
            this.paddingDegrees
        );

        return {
            visible: true,

            minLatitude,
            maxLatitude,

            minLongitude,
            maxLongitude,

            crossesAntimeridian:
                minLongitude > maxLongitude,

            sampledPointCount: points.length,

            sphereRadius: this.sphereRadius
        };
    }
}
