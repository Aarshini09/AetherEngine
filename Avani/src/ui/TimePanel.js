export class TimePanel
{
    constructor()
    {
        this.element =
            document.createElement("div");

        this.element.style.position =
            "fixed";

        this.element.style.top =
            "10px";

        this.element.style.left =
            "10px";

        this.element.style.padding =
            "8px 12px";

        this.element.style.background =
            "rgba(0, 0, 0, 0.65)";

        this.element.style.color =
            "white";

        this.element.style.fontFamily =
            "monospace";

        this.element.style.fontSize =
            "14px";

        this.element.style.zIndex =
            "1000";

        document.body.appendChild(
            this.element
        );
    }

    update(time)
    {
        const currentTime =
            time.getCurrentTime();

        this.element.textContent =
            currentTime.toISOString();
    }
}