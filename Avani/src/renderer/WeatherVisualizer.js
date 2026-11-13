
import * as THREE from "three";
import { geoToCartesian } from "../gis/CoordinateConversion.js";

export class WeatherVisualizer {
    constructor(scene, earth) {
        this.scene = scene;
        this.earth = earth;

        this.points = [];
        this.era5Mesh = null;

        // Fixed temperature scale: -50 °C to +50 °C.
        // This keeps colours consistent across geographic regions.
        this.temperatureMin = -50;
        this.temperatureMax = 50;
    }

    clear() {
        for (const point of this.points) {
            this.scene.remove(point);
            point.geometry.dispose();
            point.material.dispose();
        }

        this.points = [];
    }

    clearERA5Frame() {
        if (this.era5Mesh) {
            this.scene.remove(this.era5Mesh);
            this.era5Mesh.geometry.dispose();
            this.era5Mesh.material.dispose();
            this.era5Mesh = null;
        }
    }

    displayObservations(observations, icosahedron) {
        this.clear();

        for (const observation of observations) {
            this.addObservation(observation, icosahedron);
        }
    }

    addObservation(observation, icosahedron) {
        const position = geoToCartesian(
            observation,
            this.earth.radius
        );

        observation.spatialCell = icosahedron.findCell(position);

        const geometry = new THREE.SphereGeometry(0.025, 12, 12);
        const material = new THREE.MeshBasicMaterial({
            color: 0x00ffff
        });

        const point = new THREE.Mesh(geometry, material);
        point.position.copy(position);

        this.scene.add(point);
        this.points.push(point);
    }

    displayERA5Frame(frame) {
        if (
            !frame ||
            !Array.isArray(frame.values) ||
            !Array.isArray(frame.latitudes) ||
            !Array.isArray(frame.longitudes)
        ) {
            throw new Error("Invalid ERA5 frame data.");
        }

        const { width, height } = frame;

        if (
            !Number.isInteger(width) ||
            !Number.isInteger(height) ||
            width < 2 ||
            height < 2 ||
            frame.values.length !== width * height ||
            frame.latitudes.length !== height ||
            frame.longitudes.length !== width
        ) {
            throw new Error(
                "ERA5 frame dimensions do not match its grid data."
            );
        }
        // console.log("[ERA5] Longitude diagnostics", {
        //     first: frame.longitudes[0],
        //     second: frame.longitudes[1],
        //     middle: frame.longitudes[Math.floor(width / 2)],
        //     last: frame.longitudes[width - 1],
        //     zeroIndex: frame.longitudes.findIndex(
        //         longitude => Math.abs(longitude) < 1e-6
        //     ),
        //     nearZero: frame.longitudes.filter(
        //         longitude => Math.abs(longitude) < 1
        //     )
        // });

        const vertexCount = width * height;
        const positions = new Float32Array(vertexCount * 3);
        const colors = new Float32Array(vertexCount * 3);
        const valid = new Uint8Array(vertexCount);

        const color = new THREE.Color();
        const surfaceRadius = this.earth.radius * 1.003;
        const colorRange = this.temperatureMax - this.temperatureMin;

        let validCount = 0;

        for (let row = 0; row < height; row++) {
            for (let column = 0; column < width; column++) {
                const index = row * width + column;
                const value = frame.values[index];
                const offset = index * 3;

                const position = geoToCartesian(
                    {
                        latitude: frame.latitudes[row],
                        longitude: frame.longitudes[column],
                        height: surfaceRadius - this.earth.radius
                    },
                    this.earth.radius
                );

                positions[offset] = position.x;
                positions[offset + 1] = position.y;
                positions[offset + 2] = position.z;

                if (!Number.isFinite(value)) {
                    continue;
                }

                valid[index] = 1;
                validCount++;

                // Fixed scale: same temperature -> same colour.
                const normalized = THREE.MathUtils.clamp(
                    (value - this.temperatureMin) / colorRange,
                    0,
                    1
                );

                // Blue -> cyan -> green -> yellow -> red.
                color.setHSL(
                    0.66 * (1 - normalized),
                    1.0,
                    0.5
                );

                colors[offset] = color.r;
                colors[offset + 1] = color.g;
                colors[offset + 2] = color.b;
            }
        }

        if (validCount === 0) {
            console.warn(
                "[ERA5] Frame contains no valid values; keeping previous frame."
            );
            return;
        }

        const indices = [];

        for (let row = 0; row < height - 1; row++) {
            for (let column = 0; column < width - 1; column++) {
                const topLeft = row * width + column;
                const topRight = topLeft + 1;
                const bottomLeft = topLeft + width;
                const bottomRight = bottomLeft + 1;

                if (
                    !valid[topLeft] ||
                    !valid[topRight] ||
                    !valid[bottomLeft] ||
                    !valid[bottomRight]
                ) {
                    continue;
                }

                indices.push(
                    topLeft, bottomLeft, topRight,
                    topRight, bottomLeft, bottomRight
                );
            }
        }

        if (indices.length === 0) {
            console.warn(
                "[ERA5] No valid grid cells; keeping previous frame."
            );
            return;
        }

        const geometry = new THREE.BufferGeometry();

        geometry.setAttribute(
            "position",
            new THREE.BufferAttribute(positions, 3)
        );

        geometry.setAttribute(
            "color",
            new THREE.BufferAttribute(colors, 3)
        );

        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        // Opaque surface: remove alpha blending and transparency.
        const material = new THREE.MeshBasicMaterial({
            vertexColors: true,
            side: THREE.DoubleSide,
            transparent: false,
            opacity: 1.0,
            depthWrite: true
        });

        const nextMesh = new THREE.Mesh(geometry, material);

        nextMesh.userData = {
            variable: frame.variable,
            time: frame.time,
            unit: frame.unit,
            width,
            height,
            colorScaleMin: this.temperatureMin,
            colorScaleMax: this.temperatureMax,
            validCount
        };

        // Replace the previous ERA5 mesh only after building the new one.
        const previousMesh = this.era5Mesh;

        this.scene.add(nextMesh);
        this.era5Mesh = nextMesh;

        if (previousMesh) {
            this.scene.remove(previousMesh);
            previousMesh.geometry.dispose();
            previousMesh.material.dispose();
        }

        console.log("[ERA5] Geographic mesh displayed", {
            variable: frame.variable,
            time: frame.time,
            unit: frame.unit,
            grid: `${width} × ${height}`,
            triangles: indices.length / 3,
            validValues: validCount,
            colorScale: `${this.temperatureMin} to ${this.temperatureMax} °C`
        });
    }
}
