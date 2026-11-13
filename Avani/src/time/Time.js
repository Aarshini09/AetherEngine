export class Time
{
    constructor()
    {
        this.currentTime =
            new Date();

        this.previousRealTime =
            performance.now();

        this.deltaTime =
            0.0;

        this.elapsedTime =
            0.0;

        this.timeScale =
            1.0;
    }

    update()
    {
        const currentRealTime =
            performance.now();

        this.deltaTime =
            (
                currentRealTime -
                this.previousRealTime
            ) / 1000.0;

        this.previousRealTime =
            currentRealTime;

        this.elapsedTime +=
            this.deltaTime *
            this.timeScale;

        this.currentTime =
            new Date(
                this.currentTime.getTime() +
                this.deltaTime *
                this.timeScale *
                1000.0
            );
    }

    getCurrentTime()
    {
        return this.currentTime;
    }

    getDeltaTime()
    {
        return this.deltaTime;
    }

    getElapsedTime()
    {
        return this.elapsedTime;
    }

    setTimeScale(scale)
    {
        this.timeScale =
            scale;
    }

    getTimeScale()
    {
        return this.timeScale;
    }
}