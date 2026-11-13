import * as THREE from "three";

export class IcosahedronVisualizer {
    constructor(
        scene,
        icosahedron
    ) {
        this.scene = scene;

        this.icosahedron =
            icosahedron;

        this.vertexPoints = null;

        this.edgeLines = null;

        this.faceMesh = null;

        this.cellCenterPoints = null;

        this.highlightMesh = null;
        this.highlightMaterial = null;
        this.build();
    }

    build() {
        this.createVertices();

        this.createEdges();

        this.createFaces();

        this.createCellCenters();

        this.createHighlight();
    }

    createVertices() {
        const geometry =
            new THREE.BufferGeometry();

        const positions = [];

        for (
            const vertex of
            this.icosahedron.vertices
        ) {
            positions.push(
                vertex.x,
                vertex.y,
                vertex.z
            );
        }

        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );

        const material =
            new THREE.PointsMaterial({
                color: 0xff0000,
                size: 0.025
            });

        this.vertexPoints =
            new THREE.Points(
                geometry,
                material
            );

        this.scene.add(
            this.vertexPoints
        );
    }

    createEdges() {
        const geometry =
            new THREE.BufferGeometry();

        const positions = [];

        for (
            const edge of
            this.icosahedron.edges
        ) {
            const start =
                this.icosahedron.vertices[
                edge[0]
                ];

            const end =
                this.icosahedron.vertices[
                edge[1]
                ];

            positions.push(
                start.x,
                start.y,
                start.z,

                end.x,
                end.y,
                end.z
            );
        }

        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );

        const material =
            new THREE.LineBasicMaterial({
                color: 0xffffff
            });

        this.edgeLines =
            new THREE.LineSegments(
                geometry,
                material
            );

        this.scene.add(
            this.edgeLines
        );
    }

    createFaces() {
        const geometry =
            new THREE.BufferGeometry();

        const positions = [];

        for (
            const face of
            this.icosahedron.faces
        ) {
            const a =
                this.icosahedron.vertices[
                face[0]
                ];

            const b =
                this.icosahedron.vertices[
                face[1]
                ];

            const c =
                this.icosahedron.vertices[
                face[2]
                ];

            positions.push(
                a.x,
                a.y,
                a.z,

                b.x,
                b.y,
                b.z,

                c.x,
                c.y,
                c.z
            );
        }

        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );

        const material =
            new THREE.MeshBasicMaterial({
                transparent: true,
                opacity: 0.15,
                side: THREE.DoubleSide
            });

        this.faceMesh =
            new THREE.Mesh(
                geometry,
                material
            );

        this.scene.add(
            this.faceMesh
        );
    }

    createCellCenters() {
        const geometry =
            new THREE.BufferGeometry();

        const positions = [];

        for (
            const cell of
            this.icosahedron.cells
        ) {
            if (
                cell.center === null
            ) {
                continue;
            }

            positions.push(
                cell.center.x,
                cell.center.y,
                cell.center.z
            );
        }

        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );

        const material =
            new THREE.PointsMaterial({
                color: 0xffff00,
                size: 0.035
            });

        this.cellCenterPoints =
            new THREE.Points(
                geometry,
                material
            );

        this.scene.add(
            this.cellCenterPoints
        );
    }
    createHighlight() {
        const geometry =
            new THREE.BufferGeometry();

        const material =
            new THREE.MeshBasicMaterial({
                transparent: true,
                opacity: 0.5,
                side: THREE.DoubleSide
            });

        this.highlightMesh =
            new THREE.Mesh(
                geometry,
                material
            );

        this.highlightMesh.visible = false;

        this.scene.add(
            this.highlightMesh
        );
    }
    highlightCell(cell) {
        if (cell === null) {
            this.highlightMesh.visible = false;

            return;
        }

        const a =
            this.icosahedron.vertices[
            cell.vertices[0]
            ];

        const b =
            this.icosahedron.vertices[
            cell.vertices[1]
            ];

        const c =
            this.icosahedron.vertices[
            cell.vertices[2]
            ];

        const positions = [

            a.x, a.y, a.z,

            b.x, b.y, b.z,

            c.x, c.y, c.z
        ];

        const geometry =
            new THREE.BufferGeometry();

        geometry.setAttribute(
            "position",
            new THREE.Float32BufferAttribute(
                positions,
                3
            )
        );

        geometry.computeVertexNormals();

        this.highlightMesh.geometry.dispose();

        this.highlightMesh.geometry =
            geometry;

        this.highlightMesh.visible = true;
    }
}