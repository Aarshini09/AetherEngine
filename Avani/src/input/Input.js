export class Input
{
    constructor(element)
    {
        this.element = element;

        this.keys = new Set();

        this.mouse = {
            x: 0,
            y: 0,
            deltaX: 0,
            deltaY: 0,
            leftDown: false
        };

        this.wheelDelta = 0;

        this.initialize();
    }

    initialize()
    {
        window.addEventListener(
            "keydown",
            (event) =>
            {
                this.keys.add(event.code);

                if (
                    event.code.startsWith("Arrow")
                )
                {
                    event.preventDefault();
                }
            }
        );

        window.addEventListener(
            "keyup",
            (event) =>
            {
                this.keys.delete(event.code);
            }
        );

        this.element.addEventListener(
            "mousedown",
            (event) =>
            {
                if (event.button === 0)
                {
                    this.mouse.leftDown = true;

                    this.mouse.x = event.clientX;
                    this.mouse.y = event.clientY;
                }
            }
        );

        window.addEventListener(
            "mouseup",
            (event) =>
            {
                if (event.button === 0)
                {
                    this.mouse.leftDown = false;
                }
            }
        );

        window.addEventListener(
            "mousemove",
            (event) =>
            {
                if (!this.mouse.leftDown)
                {
                    return;
                }

                const deltaX =
                    event.clientX - this.mouse.x;

                const deltaY =
                    event.clientY - this.mouse.y;

                this.mouse.deltaX += deltaX;
                this.mouse.deltaY += deltaY;

                this.mouse.x = event.clientX;
                this.mouse.y = event.clientY;
            }
        );

        this.element.addEventListener(
            "wheel",
            (event) =>
            {
                event.preventDefault();

                this.wheelDelta += event.deltaY;
            },
            {
                passive: false
            }
        );
    }

    isKeyDown(code)
    {
        return this.keys.has(code);
    }

    consumeMouseDelta()
    {
        const delta = {
            x: this.mouse.deltaX,
            y: this.mouse.deltaY
        };

        this.mouse.deltaX = 0;
        this.mouse.deltaY = 0;

        return delta;
    }

    consumeWheel()
    {
        const value = this.wheelDelta;

        this.wheelDelta = 0;

        return value;
    }
}