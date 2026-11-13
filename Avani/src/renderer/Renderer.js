
import * as THREE from "three";

export class Renderer
{
    constructor(container = document.body)
    {
        this.container = container;

        this.renderer = new THREE.WebGLRenderer({
            antialias: true
        });

        this.renderer.setPixelRatio(
            window.devicePixelRatio
        );

        this.renderer.domElement.style.display = "block";
        this.renderer.domElement.style.width = "100%";
        this.renderer.domElement.style.height = "100%";

        this.container.appendChild(
            this.renderer.domElement
        );

        this.resize(
            this.container.clientWidth,
            this.container.clientHeight
        );
    }

    render(scene, camera)
    {
        this.renderer.render(
            scene,
            camera.camera
        );
    }

    resize(width, height)
    {
        const safeWidth = Math.max(1, width);
        const safeHeight = Math.max(1, height);

        this.renderer.setSize(
            safeWidth,
            safeHeight,
            false
        );
    }
}
