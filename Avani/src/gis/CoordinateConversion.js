import * as THREE from "three";


export function geoToCartesian(
    coordinate,
    earthRadius
)
{
    const longitude =
        THREE.MathUtils.degToRad(
            coordinate.longitude
        );

    const latitude =
        THREE.MathUtils.degToRad(
            coordinate.latitude
        );

    const radius =
        earthRadius +
        coordinate.height;

    const x =
        radius *
        Math.cos(latitude) *
        Math.cos(longitude);

    const y =
        radius *
        Math.sin(latitude);

    const z =
        radius *
        Math.cos(latitude) *
        Math.sin(longitude);

    return new THREE.Vector3(
        x,
        y,
        z
    );
}


export function cartesianToGeo(
    position,
    earthRadius
)
{
    const radius =
        position.length();

    const latitude =
        Math.asin(
            position.y / radius
        );

    const longitude =
        Math.atan2(
            position.z,
            position.x
        );

    return {
        longitude:
            THREE.MathUtils.radToDeg(
                longitude
            ),

        latitude:
            THREE.MathUtils.radToDeg(
                latitude
            ),

        height:
            radius - earthRadius
    };
}


export function raySphereIntersection(
    rayOrigin,
    rayDirection,
    sphereRadius
)
{
    const direction =
        rayDirection.clone().normalize();

    const a =
        direction.dot(direction);

    const b =
        2.0 *
        rayOrigin.dot(direction);

    const c =
        rayOrigin.dot(rayOrigin) -
        sphereRadius * sphereRadius;

    const discriminant =
        b * b -
        4.0 * a * c;

    if (discriminant < 0.0)
    {
        return null;
    }

    const sqrtDiscriminant =
        Math.sqrt(discriminant);

    const t0 =
        (-b - sqrtDiscriminant) /
        (2.0 * a);

    const t1 =
        (-b + sqrtDiscriminant) /
        (2.0 * a);

    let t = Infinity;

    if (t0 >= 0.0)
    {
        t = t0;
    }

    if (
        t1 >= 0.0 &&
        t1 < t
    )
    {
        t = t1;
    }

    if (!Number.isFinite(t))
    {
        return null;
    }

    return rayOrigin
        .clone()
        .add(
            direction.multiplyScalar(t)
        );
}