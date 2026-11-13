import * as THREE from "three";

export class OrbitController
{
    constructor(camera, input)
    {
        this.camera = camera;
        this.input = input;

        // ==================================================
        // EARTH / WORLD ORIGIN
        // ==================================================

        // The Earth NEVER moves.
        // The orbit target is always the world origin.

        this.target =
            new THREE.Vector3(
                0.0,
                0.0,
                0.0
            );


        // ==================================================
        // ORBIT STATE
        // ==================================================

        this.distance = 3.0;

        // Initial longitude around Earth.
        this.yaw =
            Math.PI / 2.0;

        // Initial latitude.
        this.pitch = 0.0;


        // ==================================================
        // CONTROL SETTINGS
        // ==================================================

        this.rotateSpeed = 0.005;

        this.keyboardRotateSpeed = 1.5;

        this.zoomSpeed = 0.001;


        // ==================================================
        // LIMITS
        // ==================================================

        this.minDistance = 1.05;

        this.maxDistance = 20.0;

        this.minPitch =
            THREE.MathUtils.degToRad(-89.0);

        this.maxPitch =
            THREE.MathUtils.degToRad(89.0);


        // ==================================================
        // INITIAL CAMERA
        // ==================================================

        this.updateCamera();
    }


    // ======================================================
    // UPDATE
    // ======================================================

    update(deltaTime)
    {
        this.handleMouse();

        this.handleKeyboard(deltaTime);

        this.handleWheel();

        this.updateCamera();
    }


    // ======================================================
    // MOUSE ORBIT
    // ======================================================

    handleMouse()
    {
        const delta =
            this.input.consumeMouseDelta();


        // --------------------------------------------------
        // Horizontal mouse movement
        //
        // Drag LEFT  -> globe moves LEFT
        // Drag RIGHT -> globe moves RIGHT
        // --------------------------------------------------

        this.yaw +=
            delta.x *
            this.rotateSpeed;


        // --------------------------------------------------
        // Vertical mouse movement
        //
        // Drag UP   -> move toward North
        // Drag DOWN -> move toward South
        // --------------------------------------------------

        this.pitch +=
            delta.y *
            this.rotateSpeed;


        // --------------------------------------------------
        // Keep latitude inside valid orbit range
        // --------------------------------------------------

        this.pitch =
            THREE.MathUtils.clamp(
                this.pitch,
                this.minPitch,
                this.maxPitch
            );
    }


    // ======================================================
    // MOUSE WHEEL ZOOM
    // ======================================================

    handleWheel()
    {
        const wheel =
            this.input.consumeWheel();


        if (wheel === 0)
        {
            return;
        }


        this.distance *=
            Math.exp(
                wheel *
                this.zoomSpeed
            );


        this.distance =
            THREE.MathUtils.clamp(
                this.distance,
                this.minDistance,
                this.maxDistance
            );
    }


    // ======================================================
    // KEYBOARD
    // ======================================================

    handleKeyboard(deltaTime)
    {
        const rotateAmount =
            this.keyboardRotateSpeed *
            deltaTime;


        // --------------------------------------------------
        // LONGITUDE
        // --------------------------------------------------

        if (
            this.input.isKeyDown(
                "ArrowRight"
            )
        )
        {
            this.yaw +=
                rotateAmount;
        }


        if (
            this.input.isKeyDown(
                "ArrowLeft"
            )
        )
        {
            this.yaw -=
                rotateAmount;
        }


        // --------------------------------------------------
        // LATITUDE
        // --------------------------------------------------

        if (
            this.input.isKeyDown(
                "ArrowUp"
            )
        )
        {
            this.pitch +=
                rotateAmount;
        }


        if (
            this.input.isKeyDown(
                "ArrowDown"
            )
        )
        {
            this.pitch -=
                rotateAmount;
        }


        // --------------------------------------------------
        // KEYBOARD ZOOM
        //
        // + -> Zoom In
        // - -> Zoom Out
        // --------------------------------------------------

        if (
            this.input.isKeyDown("Equal") ||
            this.input.isKeyDown("NumpadAdd")
        )
        {
            this.distance *=
                Math.pow(
                    0.25,
                    deltaTime
                );
        }


        if (
            this.input.isKeyDown("Minus") ||
            this.input.isKeyDown("NumpadSubtract")
        )
        {
            this.distance *=
                Math.pow(
                    4.0,
                    deltaTime
                );
        }


        // --------------------------------------------------
        // Clamp latitude
        // --------------------------------------------------

        this.pitch =
            THREE.MathUtils.clamp(
                this.pitch,
                this.minPitch,
                this.maxPitch
            );


        // --------------------------------------------------
        // Clamp distance
        // --------------------------------------------------

        this.distance =
            THREE.MathUtils.clamp(
                this.distance,
                this.minDistance,
                this.maxDistance
            );
    }


    // ======================================================
    // CAMERA POSITION
    // ======================================================

    updateCamera()
    {
        const cosPitch =
            Math.cos(this.pitch);


        // --------------------------------------------------
        // Spherical orbit coordinates
        //
        // X = longitude direction
        // Y = latitude direction
        // Z = longitude direction
        // --------------------------------------------------

        const x =
            this.distance *
            cosPitch *
            Math.cos(this.yaw);


        const y =
            this.distance *
            Math.sin(this.pitch);


        const z =
            this.distance *
            cosPitch *
            Math.sin(this.yaw);


        // --------------------------------------------------
        // Camera position
        //
        // Earth remains at world origin.
        // --------------------------------------------------

        this.camera.camera.position.set(
            this.target.x + x,
            this.target.y + y,
            this.target.z + z
        );


        // --------------------------------------------------
        // Camera always looks at Earth center.
        // --------------------------------------------------

        this.camera.camera.lookAt(
            this.target
        );
    }


    // ======================================================
    // GO TO GEOGRAPHIC LOCATION
    // ======================================================

    goToLocation(position)
    {
        /*
         * position:
         *
         * A Cartesian position on the Earth.
         *
         * We do NOT move the Earth.
         * We do NOT move the orbit target.
         *
         * We only calculate the yaw/pitch required
         * to place the camera over that location.
         */


        // --------------------------------------------------
        // Convert position into a unit direction.
        // --------------------------------------------------

        const direction =
            position
                .clone()
                .normalize();


        // --------------------------------------------------
        // Longitude
        // --------------------------------------------------

        this.yaw =
            Math.atan2(
                direction.z,
                direction.x
            );


        // --------------------------------------------------
        // Latitude
        // --------------------------------------------------

        this.pitch =
            Math.asin(
                THREE.MathUtils.clamp(
                    direction.y,
                    -1.0,
                    1.0
                )
            );


        // --------------------------------------------------
        // Recalculate camera position.
        // --------------------------------------------------

        this.updateCamera();
    }
}