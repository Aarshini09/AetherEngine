export class TimeController {
    constructor(options = {}) {
        // --------------------------------------------------
        // Loaded visualization frames
        // --------------------------------------------------

        this.frames = [];
        this.currentIndex = 0;
        this.currentTime = null;

        // --------------------------------------------------
        // Generalized temporal state
        // --------------------------------------------------

        this.referenceTime = this._toTimestamp(
            options.referenceTime ?? new Date()
        );

        this.selectedTime = this.referenceTime;

        // Signed offset from the reference time, in seconds.
        // Negative = past, zero = reference, positive = future.
        this.timeOffset = 0;

        this.navigationMode = "frames";

        // Default navigation step: 6 hours, matching ERA5.
        this.stepSeconds = options.stepSeconds ?? 6 * 60 * 60;

        // Optional temporal limits, expressed as timestamps.
        this.pastLimit = null;
        this.futureLimit = null;

        // --------------------------------------------------
        // Playback
        // --------------------------------------------------

        this.playing = false;
        this.playbackSpeed = options.playbackSpeed ?? 1.0;
        this.frameInterval = options.frameInterval ?? 750;

        this._timer = null;
        this._listeners = [];

        console.log("TimeController initialized.");
    }

    // --------------------------------------------------
    // Loaded frame timeline
    // --------------------------------------------------

    setFrames(frames) {
        this.stop();

        if (!Array.isArray(frames)) {
            console.warn(
                "TimeController: frames must be an array."
            );

            this.frames = [];
            this.currentIndex = 0;
            this.currentTime = null;
            this._notify();
            return;
        }

        this.frames = frames;
        this.currentIndex = 0;

        if (this.frames.length > 0) {
            this.currentTime = this.frames[0].time;
            this.selectedTime = this._toTimestamp(
                this.currentTime
            );
            this.timeOffset =
                (this.selectedTime - this.referenceTime) / 1000;
        }
        else {
            this.currentTime = null;
        }

        this.navigationMode = "frames";
        this._notify();
    }

    
getCurrentFrame()
{
    if (
        this.frames.length === 0 ||
        this.currentIndex < 0 ||
        this.currentIndex >= this.frames.length
    )
    {
        return null;
    }

    return this.frames[this.currentIndex] ?? null;
}


    getCurrentTime() {
        return this.currentTime;
    }

    getCurrentIndex() {
        return this.currentIndex;
    }

    getFrameCount() {
        return this.frames.length;
    }

    setFrame(index) {
        if (this.frames.length === 0) {
            return;
        }

        const numericIndex = Number(index);

        if (!Number.isFinite(numericIndex)) {
            return;
        }

        const clampedIndex = Math.max(
            0,
            Math.min(
                Math.trunc(numericIndex),
                this.frames.length - 1
            )
        );

        this.currentIndex = clampedIndex;
        this.currentTime = this.frames[clampedIndex].time;
        this.selectedTime = this._toTimestamp(
            this.currentTime
        );

        this.timeOffset =
            (this.selectedTime - this.referenceTime) / 1000;

        this.navigationMode = "frames";
        this._notify();
    }

    next() {
        if (this.frames.length === 0) {
            return;
        }

        if (this.currentIndex < this.frames.length - 1) {
            this.setFrame(this.currentIndex + 1);
        }
        else {
            this.pause();
        }
    }

    previous() {
        if (this.frames.length === 0) {
            return;
        }

        if (this.currentIndex > 0) {
            this.setFrame(this.currentIndex - 1);
        }
    }

    first() {
        if (this.frames.length > 0) {
            this.setFrame(0);
        }
    }

    last() {
        if (this.frames.length > 0) {
            this.setFrame(this.frames.length - 1);
        }
    }

    // --------------------------------------------------
    // Reference-time model
    // --------------------------------------------------

    setReferenceTime(value) {
        this.referenceTime = this._toTimestamp(value);
        this._updateOffset();
        this._notify();
    }

    getReferenceTime() {
        return new Date(this.referenceTime);
    }

    setSelectedTime(value) {
        const timestamp = this._toTimestamp(value);

        if (!this._isWithinLimits(timestamp)) {
            return false;
        }

        this.pause();

        this.selectedTime = timestamp;
        this.timeOffset =
            (timestamp - this.referenceTime) / 1000;

        this.navigationMode = "reference";

        // A reference-time selection may not have a loaded frame.
        this.currentIndex = this._findFrameIndex(timestamp);

        if (this.currentIndex >= 0) {
            this.currentTime = this.frames[this.currentIndex].time;
        }
        else {
            this.currentTime = null;
        }
        this._notify();
        return true;
    }

    setTimeOffset(seconds) {
        const numericOffset = Number(seconds);

        if (!Number.isFinite(numericOffset)) {
            return false;
        }

        const timestamp =
            this.referenceTime + numericOffset * 1000;

        return this.setSelectedTime(timestamp);
    }

    getSelectedTime() {
        return new Date(this.selectedTime);
    }

    getTimeOffset() {
        return this.timeOffset;
    }

    setStepSeconds(seconds) {
        const value = Number(seconds);

        if (!Number.isFinite(value) || value <= 0) {
            return;
        }

        this.stepSeconds = value;
        this._notify();
    }

    getStepSeconds() {
        return this.stepSeconds;
    }

    setTemporalLimits(pastLimit = null, futureLimit = null) {
        this.pastLimit = pastLimit === null
            ? null
            : this._toTimestamp(pastLimit);

        this.futureLimit = futureLimit === null
            ? null
            : this._toTimestamp(futureLimit);

        this._notify();
    }

    stepBackward() {
        return this.setSelectedTime(
            this.selectedTime - this.stepSeconds * 1000
        );
    }

    stepForward() {
        return this.setSelectedTime(
            this.selectedTime + this.stepSeconds * 1000
        );
    }

    // --------------------------------------------------
    // Playback
    // --------------------------------------------------

    play() {
        if (this.playing) {
            return;
        }

        if (this.frames.length <= 1) {
            return;
        }

        if (this.currentIndex >= this.frames.length - 1) {
            this.first();
        }

        this.playing = true;
        this._notify();
        this._startTimer();
    }

    pause() {
        if (!this.playing) {
            return;
        }

        this.playing = false;
        this._stopTimer();
        this._notify();
    }

    stop() {
        this.playing = false;
        this._stopTimer();
    }

    togglePlayback() {
        if (this.playing) {
            this.pause();
        }
        else {
            this.play();
        }
    }

    setPlaybackSpeed(speed) {
        const numericSpeed = Number(speed);

        if (
            !Number.isFinite(numericSpeed) ||
            numericSpeed <= 0
        ) {
            return;
        }

        this.playbackSpeed = numericSpeed;

        if (this.playing) {
            this._startTimer();
        }
    }

    getPlaybackSpeed() {
        return this.playbackSpeed;
    }

    _startTimer() {
        this._stopTimer();

        const interval =
            this.frameInterval / this.playbackSpeed;

        this._timer = setInterval(
            () => {
                if (
                    this.currentIndex >=
                    this.frames.length - 1
                ) {
                    this.pause();
                    return;
                }

                this.next();
            },
            interval
        );
    }

    _stopTimer() {
        if (this._timer !== null) {
            clearInterval(this._timer);
            this._timer = null;
        }
    }

    // --------------------------------------------------
    // Listener system
    // --------------------------------------------------

    addListener(listener) {
        if (
            typeof listener !== "function" ||
            this._listeners.includes(listener)
        ) {
            return;
        }

        this._listeners.push(listener);
    }

    removeListener(listener) {
        this._listeners = this._listeners.filter(
            existingListener =>
                existingListener !== listener
        );
    }

    _notify() {
        const state = {
            index: this.currentIndex,
            time: this.currentTime,
            frame: this.getCurrentFrame(),
            frameCount: this.frames.length,
            playing: this.playing,

            referenceTime: new Date(this.referenceTime),
            selectedTime: new Date(this.selectedTime),
            timeOffset: this.timeOffset,
            navigationMode: this.navigationMode,
            stepSeconds: this.stepSeconds
        };

        for (const listener of [...this._listeners]) {
            listener(state);
        }
    }

    isPlaying() {
        return this.playing;
    }

    // --------------------------------------------------
    // Internal helpers
    // --------------------------------------------------

    _toTimestamp(value) {
        const timestamp = value instanceof Date
            ? value.getTime()
            : new Date(value).getTime();

        if (!Number.isFinite(timestamp)) {
            throw new Error(
                `TimeController: invalid timestamp: ${value}`
            );
        }

        return timestamp;
    }

    _updateOffset() {
        this.timeOffset =
            (this.selectedTime - this.referenceTime) / 1000;
    }

    _isWithinLimits(timestamp) {
        if (
            this.pastLimit !== null &&
            timestamp < this.pastLimit
        ) {
            return false;
        }

        if (
            this.futureLimit !== null &&
            timestamp > this.futureLimit
        ) {
            return false;
        }

        return true;
    }

    _findFrameIndex(timestamp) {
        return this.frames.findIndex(
            frame =>
                this._toTimestamp(frame.time) === timestamp
        );
    }

    destroy() {
        this.stop();
        this._listeners = [];
        this.frames = [];
        this.currentIndex = 0;
        this.currentTime = null;
    }
}
