export class VisualizationData {
    constructor(data) {
        if (!data) {
            throw new Error(
                "Visualization data cannot be null."
            );
        }

        this.variable = data.variable ?? null;

        this.startTime =
            data.start_time ?? null;

        this.endTime =
            data.end_time ?? null;

        this.frameCount =
            data.frame_count ?? 0;

        this.frames =
            Array.isArray(data.frames)
                ? data.frames
                : [];

        this.tracks =
            Array.isArray(data.tracks)
                ? data.tracks
                : [];

        this.events =
            Array.isArray(data.events)
                ? data.events
                : [];
    }

    getFrameCount() {
        return this.frames.length;
    }

    getFrame(index) {
        if (
            index < 0 ||
            index >= this.frames.length
        ) {
            throw new RangeError(
                `Invalid visualization frame index: ${index}`
            );
        }

        return this.frames[index];
    }

    getFrameAtTime(time) {
        return this.frames.find(
            frame => frame.time === time
        ) ?? null;
    }

    getFirstFrame() {
        if (this.frames.length === 0) {
            return null;
        }

        return this.frames[0];
    }

    getLastFrame() {
        if (this.frames.length === 0) {
            return null;
        }

        return this.frames[
            this.frames.length - 1
        ];
    }

    getTracks() {
        return this.tracks;
    }

    getEvents() {
        return this.events;
    }

    getAnomaliesAtFrame(index) {
        const frame =
            this.getFrame(index);

        return Array.isArray(frame.anomalies)
            ? frame.anomalies
            : [];
    }

    getRegionsAtFrame(index) {
        const frame =
            this.getFrame(index);

        return Array.isArray(frame.regions)
            ? frame.regions
            : [];
    }

    getSummary() {
        return {
            variable: this.variable,
            startTime: this.startTime,
            endTime: this.endTime,
            frameCount: this.getFrameCount(),
            trackCount: this.tracks.length,
            eventCount: this.events.length
        };
    }
}