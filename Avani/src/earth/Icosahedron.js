import * as THREE from "three";

import { GeoCell } from "./GeoCell.js";

export class Icosahedron {
    constructor(radius = 1.0) {
        this.radius = radius;

        this.level = 0;

        this.vertices = [];
        this.edges = [];
        this.faces = [];

        this.cells = [];

        this.nextCellId = 0;

        this.build();
    }

    build() {
        this.createVertices();
        this.createEdges();
        this.createFaces();
        this.createCells();
    }

    createVertices() {
        const phi =
            (1.0 + Math.sqrt(5.0)) / 2.0;

        const rawVertices = [

            // (0, ±1, ±φ)
            new THREE.Vector3(0, 1, phi),
            new THREE.Vector3(0, -1, phi),
            new THREE.Vector3(0, 1, -phi),
            new THREE.Vector3(0, -1, -phi),

            // (±1, ±φ, 0)
            new THREE.Vector3(1, phi, 0),
            new THREE.Vector3(-1, phi, 0),
            new THREE.Vector3(1, -phi, 0),
            new THREE.Vector3(-1, -phi, 0),

            // (±φ, 0, ±1)
            new THREE.Vector3(phi, 0, 1),
            new THREE.Vector3(phi, 0, -1),
            new THREE.Vector3(-phi, 0, 1),
            new THREE.Vector3(-phi, 0, -1)
        ];

        for (const vertex of rawVertices) {
            vertex.normalize();

            vertex.multiplyScalar(
                this.radius
            );

            this.vertices.push(
                vertex
            );
        }
    }

    createEdges() {
        let shortestDistance =
            Infinity;

        for (
            let i = 0;
            i < this.vertices.length;
            i++
        ) {
            for (
                let j = i + 1;
                j < this.vertices.length;
                j++
            ) {
                const distance =
                    this.vertices[i].distanceTo(
                        this.vertices[j]
                    );

                if (
                    distance <
                    shortestDistance
                ) {
                    shortestDistance =
                        distance;
                }
            }
        }

        const tolerance =
            0.000001;

        for (
            let i = 0;
            i < this.vertices.length;
            i++
        ) {
            for (
                let j = i + 1;
                j < this.vertices.length;
                j++
            ) {
                const distance =
                    this.vertices[i].distanceTo(
                        this.vertices[j]
                    );

                if (
                    Math.abs(
                        distance -
                        shortestDistance
                    ) < tolerance
                ) {
                    this.edges.push([
                        i,
                        j
                    ]);
                }
            }
        }
    }

    createFaces() {
        const edgeSet =
            new Set();

        for (const edge of this.edges) {
            const a = edge[0];
            const b = edge[1];

            edgeSet.add(`${a}:${b}`);
            edgeSet.add(`${b}:${a}`);
        }

        for (
            let a = 0;
            a < this.vertices.length;
            a++
        ) {
            for (
                let b = a + 1;
                b < this.vertices.length;
                b++
            ) {
                if (
                    !edgeSet.has(`${a}:${b}`)
                ) {
                    continue;
                }

                for (
                    let c = b + 1;
                    c < this.vertices.length;
                    c++
                ) {
                    const ab =
                        edgeSet.has(`${a}:${b}`);

                    const ac =
                        edgeSet.has(`${a}:${c}`);

                    const bc =
                        edgeSet.has(`${b}:${c}`);

                    if (
                        ab &&
                        ac &&
                        bc
                    ) {
                        this.faces.push([
                            a,
                            b,
                            c
                        ]);
                    }
                }
            }
        }
    }

    createCells() {
        this.cells = [];

        this.nextCellId = 0;

        for (
            const face of this.faces
        ) {
            const cell =
                new GeoCell(
                    this.nextCellId++,
                    face,
                    this.level
                );

            this.cells.push(
                cell
            );
        }

        this.calculateCellCenters();
    }

    subdivide() {
        const newFaces = [];

        const midpointCache =
            new Map();

        const newCells = [];

        const getMidpoint =
            (indexA, indexB) => {
                const smaller =
                    Math.min(
                        indexA,
                        indexB
                    );

                const larger =
                    Math.max(
                        indexA,
                        indexB
                    );

                const key =
                    `${smaller}:${larger}`;

                if (
                    midpointCache.has(key)
                ) {
                    return midpointCache.get(
                        key
                    );
                }

                const vertexA =
                    this.vertices[indexA];

                const vertexB =
                    this.vertices[indexB];

                const midpoint =
                    vertexA.clone()
                        .add(vertexB)
                        .multiplyScalar(0.5);

                midpoint.normalize();

                midpoint.multiplyScalar(
                    this.radius
                );

                const newIndex =
                    this.vertices.length;

                this.vertices.push(
                    midpoint
                );

                midpointCache.set(
                    key,
                    newIndex
                );

                return newIndex;
            };

        for (
            const parentCell of this.cells
        ) {
            const a =
                parentCell.vertices[0];

            const b =
                parentCell.vertices[1];

            const c =
                parentCell.vertices[2];

            const ab =
                getMidpoint(a, b);

            const bc =
                getMidpoint(b, c);

            const ca =
                getMidpoint(c, a);

            const childFaces = [

                [a, ab, ca],

                [ab, b, bc],

                [ca, bc, c],

                [ab, bc, ca]
            ];

            const children = [];

            for (
                const face of childFaces
            ) {
                const childCell =
                    new GeoCell(
                        this.nextCellId++,
                        face,
                        this.level + 1
                    );

                parentCell.addChild(
                    childCell
                );

                children.push(
                    childCell
                );

                newFaces.push(
                    face
                );
            }

            newCells.push(
                ...children
            );
        }

        this.faces =
            newFaces;

        this.cells =
            newCells;

        this.level++;

        this.calculateCellCenters();

        this.rebuildEdges();
    }

    rebuildEdges() {
        const edgeSet =
            new Set();

        this.edges = [];

        for (
            const face of this.faces
        ) {
            const a = face[0];
            const b = face[1];
            const c = face[2];

            const faceEdges = [
                [a, b],
                [b, c],
                [c, a]
            ];

            for (
                const edge of faceEdges
            ) {
                const start =
                    Math.min(
                        edge[0],
                        edge[1]
                    );

                const end =
                    Math.max(
                        edge[0],
                        edge[1]
                    );

                const key =
                    `${start}:${end}`;

                if (
                    !edgeSet.has(key)
                ) {
                    edgeSet.add(key);

                    this.edges.push([
                        start,
                        end
                    ]);
                }
            }
        }
    }
    calculateCellCenter(cell) {
        const vertexA =
            this.vertices[
            cell.vertices[0]
            ];

        const vertexB =
            this.vertices[
            cell.vertices[1]
            ];

        const vertexC =
            this.vertices[
            cell.vertices[2]
            ];

        const center =
            vertexA.clone()
                .add(vertexB)
                .add(vertexC)
                .multiplyScalar(
                    1.0 / 3.0
                );

        center.normalize();

        center.multiplyScalar(
            this.radius
        );

        cell.setCenter(
            center
        );
    }
    calculateCellCenters() {
        for (
            const cell of this.cells
        ) {
            this.calculateCellCenter(
                cell
            );
        }
    }

    findCell(position) {
        const point =
            position.clone().normalize();

        const epsilon = 0.000001;

        for (
            const cell of this.cells
        ) {
            const a =
                this.vertices[
                    cell.vertices[0]
                ].clone().normalize();

            const b =
                this.vertices[
                    cell.vertices[1]
                ].clone().normalize();

            const c =
                this.vertices[
                    cell.vertices[2]
                ].clone().normalize();

            const ab =
                new THREE.Vector3()
                    .crossVectors(a, b);

            const bc =
                new THREE.Vector3()
                    .crossVectors(b, c);

            const ca =
                new THREE.Vector3()
                    .crossVectors(c, a);

            const sideAB =
                ab.dot(point);

            const sideBC =
                bc.dot(point);

            const sideCA =
                ca.dot(point);

            const orientation =
                ab.dot(c);

            if (orientation < 0.0) {
                if (
                    sideAB <= epsilon &&
                    sideBC <= epsilon &&
                    sideCA <= epsilon
                ) {
                    return cell;
                }
            }
            else {
                if (
                    sideAB >= -epsilon &&
                    sideBC >= -epsilon &&
                    sideCA >= -epsilon
                ) {
                    return cell;
                }
            }
        }

        return null;
    }

    getVertexCount() {
        return this.vertices.length;
    }

    getEdgeCount() {
        return this.edges.length;
    }

    getFaceCount() {
        return this.faces.length;
    }

    getCellCount() {
        return this.cells.length;
    }

    getLevel() {
        return this.level;
    }
    buildCellAdjacency() {
        for (const cell of this.cells) {
            cell.neighbors = [];
        }

        for (let i = 0; i < this.cells.length; i++) {
            for (let j = i + 1; j < this.cells.length; j++) {
                const a = this.cells[i];
                const b = this.cells[j];

                let sharedVertices = 0;

                for (const vertexA of a.vertices) {
                    if (b.vertices.includes(vertexA)) {
                        sharedVertices++;
                    }
                }

                if (sharedVertices === 2) {
                    a.addNeighbor(b);
                    b.addNeighbor(a);
                }
            }
        }
        console.log(
            "Cell 20 neighbors:",
            icosahedron.cells[20].getNeighbors()
        );
    }

}