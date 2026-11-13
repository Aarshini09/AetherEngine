import * as THREE from "three";

import {
    geoToCartesian
} from "../../gis/CoordinateConversion.js";


export class VariableGraph {

    constructor(options = {}) {

        this.radius =
            options.radius ?? 1.05;

        this.wrapLongitude =
            options.wrapLongitude ?? false;

        this.group =
            new THREE.Group();

        this.mesh = null;

        this.geometry = null;

        this.material = null;

        this.values = [];

        this.minimumValue = null;

        this.maximumValue = null;

        this.gridRows = 0;

        this.gridColumns = 0;

        this.cellCount = 0;
    }


    /*
     * --------------------------------------------------
     * Clear
     * --------------------------------------------------
     */

    clear() {

        if (this.mesh) {

            this.group.remove(
                this.mesh
            );
        }


        if (this.geometry) {

            this.geometry.dispose();
        }


        if (this.material) {

            this.material.dispose();
        }


        this.mesh = null;

        this.geometry = null;

        this.material = null;

        this.values = [];

        this.minimumValue = null;

        this.maximumValue = null;

        this.gridRows = 0;

        this.gridColumns = 0;

        this.cellCount = 0;
    }


    /*
     * --------------------------------------------------
     * Set Frame
     * --------------------------------------------------
     */

    setFrame(frame) {

        /*
         * Remove the previous frame.
         */

        this.clear();


        if (!frame) {

            console.warn(
                "VariableGraph: frame is null."
            );

            return;
        }


        if (!Array.isArray(frame.values)) {

            console.warn(
                "VariableGraph: frame contains no values."
            );

            return;
        }


        this.values =
            frame.values;


        if (this.values.length === 0) {

            console.warn(
                "VariableGraph: frame contains zero samples."
            );

            return;
        }


        /*
         * Calculate color range.
         */

        this._calculateValueRange();


        /*
         * Convert the flat sample list
         * into a rectangular geographic grid.
         */

        const grid =
            this._buildGrid();


        if (!grid) {

            console.warn(
                "VariableGraph: could not construct spatial grid."
            );

            return;
        }


        const positions = [];

        const colors = [];

        const indices = [];


        /*
         * --------------------------------------------------
         * Vertices
         * --------------------------------------------------
         *
         * Every ERA5 sample becomes one vertex.
         *
         * The vertex is positioned on the real spherical
         * Earth using latitude / longitude.
         */

        for (
            const row of grid.rows
        ) {

            for (
                const sample of row
            ) {

                const coordinate = {

                    latitude:
                        Number(
                            sample.latitude
                        ),

                    longitude:
                        Number(
                            sample.longitude
                        ),

                    height:
                        0
                };


                const position =
                    geoToCartesian(
                        coordinate,
                        this.radius
                    );


                positions.push(
                    position.x,
                    position.y,
                    position.z
                );


                const color =
                    this.valueToColor(
                        sample.value
                    );


                colors.push(
                    color.r,
                    color.g,
                    color.b
                );
            }
        }


        /*
         * --------------------------------------------------
         * Grid Cells
         * --------------------------------------------------
         *
         * Each rectangular weather-grid cell is divided
         * into two triangles.
         *
         * For a global field the final longitude column
         * connects back to the first longitude column.
         *
         * Example:
         *
         *     A ----- B
         *     |     / |
         *     |   /   |
         *     | /     |
         *     C ----- D
         *
         * becomes:
         *
         *     A ----- B
         *     | \     |
         *     |   \   |
         *     |     \ |
         *     C ----- D
         *
         */

        const columnCellCount =
            this.wrapLongitude
                ? this.gridColumns
                : this.gridColumns - 1;


        for (
            let row = 0;
            row < this.gridRows - 1;
            row++
        ) {

            for (
                let column = 0;
                column < columnCellCount;
                column++
            ) {

                /*
                 * Determine the next longitude column.
                 *
                 * Local grid:
                 *
                 *   0 → 1
                 *   1 → 2
                 *   2 → 3
                 *
                 * Global grid:
                 *
                 *   178 → 179
                 *   179 → 0
                 */

                const nextColumn =
                    this.wrapLongitude
                        ? (
                            (column + 1) %
                            this.gridColumns
                        )
                        : (
                            column + 1
                        );


                /*
                 * Four corners of the cell.
                 */

                const topLeft =
                    row *
                    this.gridColumns +
                    column;


                const topRight =
                    row *
                    this.gridColumns +
                    nextColumn;


                const bottomLeft =
                    (row + 1) *
                    this.gridColumns +
                    column;


                const bottomRight =
                    (row + 1) *
                    this.gridColumns +
                    nextColumn;


                /*
                 * First triangle.
                 */

                indices.push(
                    topLeft,
                    bottomLeft,
                    topRight
                );


                /*
                 * Second triangle.
                 */

                indices.push(
                    topRight,
                    bottomLeft,
                    bottomRight
                );


                this.cellCount++;
            }
        }


        /*
         * --------------------------------------------------
         * Geometry
         * --------------------------------------------------
         *
         * IMPORTANT:
         *
         * The geometry MUST be created before calling
         * setAttribute() or setIndex().
         */

        this.geometry =
            new THREE.BufferGeometry();


        /*
         * Position attribute.
         */

        this.geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );


        /*
         * Color attribute.
         */

        this.geometry.setAttribute(
            "color",
            new THREE.Float32BufferAttribute(
                colors,
                3
            )
        );


        /*
         * Triangle index buffer.
         */

        this.geometry.setIndex(
            indices
        );


        /*
         * Tell Three.js that the geometry contains
         * vertex colors.
         */

        this.geometry.computeBoundingSphere();


        /*
         * --------------------------------------------------
         * Material
         * --------------------------------------------------
         */

        this.material =
            new THREE.MeshBasicMaterial({

                vertexColors:
                    true,

                side:
                    THREE.DoubleSide,

                transparent:
                    true,

                opacity:
                    0.88
            });


        /*
         * --------------------------------------------------
         * Mesh
         * --------------------------------------------------
         */

        this.mesh =
            new THREE.Mesh(
                this.geometry,
                this.material
            );


        /*
         * Add the generated weather field
         * to the graph group.
         */

        this.group.add(
            this.mesh
        );
    }


    /*
     * --------------------------------------------------
     * Build Geographic Grid
     * --------------------------------------------------
     */

    _buildGrid() {

        const latitudeMap =
            new Map();


        /*
         * Group samples by latitude.
         */

        for (
            const sample of this.values
        ) {

            const latitude =
                Number(
                    sample.latitude
                );


            const longitude =
                Number(
                    sample.longitude
                );


            const value =
                Number(
                    sample.value
                );


            /*
             * Ignore invalid samples.
             */

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude) ||
                !Number.isFinite(value)
            ) {

                continue;
            }


            /*
             * Create latitude row if necessary.
             */

            if (
                !latitudeMap.has(
                    latitude
                )
            ) {

                latitudeMap.set(
                    latitude,
                    []
                );
            }


            latitudeMap
                .get(latitude)
                .push({

                    latitude,
                    longitude,
                    value
                });
        }


        /*
         * Sort latitude rows from north
         * to south.
         *
         * Example:
         *
         *   90
         *   88
         *   86
         *   ...
         *  -88
         *  -90
         */

        const latitudes =
            [...latitudeMap.keys()]
                .sort(
                    (a, b) =>
                        b - a
                );


        const rows = [];


        for (
            const latitude of latitudes
        ) {

            const row =
                latitudeMap.get(
                    latitude
                );


            /*
             * Sort longitude west → east.
             */

            row.sort(
                (a, b) =>
                    a.longitude -
                    b.longitude
            );


            rows.push(
                row
            );
        }


        /*
         * No valid rows.
         */

        if (
            rows.length === 0
        ) {

            return null;
        }


        /*
         * Number of longitude samples
         * in the first row.
         */

        const columnCount =
            rows[0].length;


        /*
         * The current renderer expects a
         * rectangular weather grid.
         */

        for (
            const row of rows
        ) {

            if (
                row.length !==
                columnCount
            ) {

                console.warn(
                    "VariableGraph: irregular grid detected."
                );

                return null;
            }
        }


        /*
         * Store grid dimensions.
         */

        this.gridRows =
            rows.length;


        this.gridColumns =
            columnCount;


        return {
            rows
        };
    }


    /*
     * --------------------------------------------------
     * Calculate Value Range
     * --------------------------------------------------
     */

    _calculateValueRange() {

        const validValues =
            this.values
                .map(
                    sample =>
                        Number(
                            sample.value
                        )
                )
                .filter(
                    value =>
                        Number.isFinite(
                            value
                        )
                );


        if (
            validValues.length === 0
        ) {

            this.minimumValue =
                0;

            this.maximumValue =
                1;

            return;
        }


        this.minimumValue =
            Math.min(
                ...validValues
            );


        this.maximumValue =
            Math.max(
                ...validValues
            );
    }


    /*
     * --------------------------------------------------
     * Convert Value → Color
     * --------------------------------------------------
     */

    valueToColor(value) {

        const numericValue =
            Number(value);


        /*
         * Invalid values become white.
         */

        if (
            !Number.isFinite(
                numericValue
            )
        ) {

            return new THREE.Color(
                0xffffff
            );
        }


        const range =
            this.maximumValue -
            this.minimumValue;


        let normalized;


        /*
         * Constant field.
         */

        if (
            range === 0
        ) {

            normalized =
                0.5;

        } else {

            normalized =
                (
                    numericValue -
                    this.minimumValue
                ) / range;
        }


        /*
         * Keep the value inside
         * the [0, 1] range.
         */

        normalized =
            THREE.MathUtils.clamp(
                normalized,
                0,
                1
            );


        const color =
            new THREE.Color();


        /*
         * --------------------------------------------------
         * Low values → Blue
         * Middle values → Green / Yellow
         * High values → Red
         * --------------------------------------------------
         */

        if (
            normalized < 0.5
        ) {

            const t =
                normalized * 2.0;


            color.setRGB(
                t,
                t,
                1.0
            );

        } else {

            const t =
                (
                    normalized -
                    0.5
                ) * 2.0;


            color.setRGB(
                1.0,
                1.0 - t,
                0.0
            );
        }


        return color;
    }


    /*
     * --------------------------------------------------
     * Accessors
     * --------------------------------------------------
     */

    getObject() {

        return this.group;
    }


    getSampleCount() {

        return this.values.length;
    }


    getMinimumValue() {

        return this.minimumValue;
    }


    getMaximumValue() {

        return this.maximumValue;
    }


    getGridRows() {

        return this.gridRows;
    }


    getGridColumns() {

        return this.gridColumns;
    }


    getCellCount() {

        return this.cellCount;
    }
}