import * as THREE from "three";

import {
    CAMERA_FOV,
    CAMERA_NEAR,
    CAMERA_FAR
} from "../core/Constants.js";

export class Camera
{
    constructor()
    {
        this.camera = new THREE.PerspectiveCamera(
            CAMERA_FOV,
            window.innerWidth / window.innerHeight,
            CAMERA_NEAR,
            CAMERA_FAR
        );

        this.camera.position.set(
            0.0,
            0.0,
            3.0
        );

        this.camera.lookAt(
            0.0,
            0.0,
            0.0
        );
    }

    resize(width, height)
    {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
    }
}