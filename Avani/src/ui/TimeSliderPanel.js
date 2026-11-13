
export class TimeSliderPanel
{
    constructor(timeController)
    {
        if (!timeController)
        {
            throw new Error("TimeSliderPanel requires a TimeController.");
        }

        this.timeController = timeController;
        this.panel = null;
        this.timelineViewport = null;
        this.timelineContent = null;
        this.ticks = null;
        this.selectedMarker = null;
        this.referenceMarker = null;
        this.coverage = null;
        this.currentTimeLabel = null;
        this.referenceInput = null;
        this.selectedInput = null;
        this.offsetLabel = null;
        this.statusLabel = null;
        this.stepLabel = null;
        this.playButton = null;
        this.speedSelect = null;
        this.zoomSelect = null;

        // Visible time span, in hours.
        this.timelineHours = 24 * 30;

        // Optional actual dataset coverage.
        this.datasetStart = null;
        this.datasetEnd = null;

        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartTime = 0;
        this.lastWidth = 0;

        this._build();

        this._listener = state => this._update(state);
        this.timeController.addListener(this._listener);

        this._update(this._getCurrentState());

        this._resizeHandler = () =>
        {
            this._renderTimeline();
        };

        window.addEventListener("resize", this._resizeHandler);
    }

    // --------------------------------------------------
    // UI construction
    // --------------------------------------------------

    _build()
    {
        this.panel = document.createElement("section");

        Object.assign(this.panel.style, {
            position: "relative",
            left: "auto",
            bottom: "auto",
            transform: "none",
            width: "100%",
            maxWidth:"1600px",
            margin:"24px auto",
            boxSizing: "border-box",
            padding: "12px 16px",
            background: "rgba(8, 12, 20, 0.96)",
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: "12px",
            backdropFilter: "blur(12px)",
            boxShadow: "0 8px 30px rgba(0,0,0,0.45)",
            color: "#f1f5f9",
            fontFamily: "Arial, Helvetica, sans-serif",
            zIndex: "10000",
            userSelect: "none"
        });

        // Header
        const header = document.createElement("div");

        Object.assign(header.style, {
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "10px",
            flexWrap: "wrap",
            marginBottom: "10px"
        });

        const title = document.createElement("strong");
        title.textContent = "AVANI · TEMPORAL NAVIGATION";
        title.style.cssText =
            "font-size:12px;letter-spacing:1px;color:#93c5fd";

        this.currentTimeLabel = document.createElement("span");
        this.currentTimeLabel.style.cssText =
            "font-size:13px;font-weight:600;font-variant-numeric:tabular-nums";

        header.append(title, this.currentTimeLabel);

        // Date controls
        const dateRow = document.createElement("div");

        Object.assign(dateRow.style, {
            display: "flex",
            alignItems: "end",
            gap: "10px",
            flexWrap: "wrap",
            marginBottom: "10px"
        });

        this.referenceInput = this._createDateInput();
        this.selectedInput = this._createDateInput();

        dateRow.append(
            this._createField("Reference time (UTC)", this.referenceInput),
            this._createField("Selected time (UTC)", this.selectedInput)
        );

        this.offsetLabel = document.createElement("span");
        this.offsetLabel.style.cssText =
            "font-size:11px;color:#cbd5e1;padding-bottom:7px";

        dateRow.appendChild(this.offsetLabel);

        this.referenceInput.addEventListener("change", () =>
        {
            if (!this.referenceInput.value) return;

            const date = this._parseInput(this.referenceInput.value);
            if (!date) return;

            this.timeController.setReferenceTime(date);
            this._renderTimeline();
        });

        this.selectedInput.addEventListener("change", () =>
        {
            if (!this.selectedInput.value) return;

            const date = this._parseInput(this.selectedInput.value);
            if (!date) return;

            if (!this.timeController.setSelectedTime(date))
            {
                this._update(this._getCurrentState());
            }
        });

        // Playback and navigation controls
        const controls = document.createElement("div");

        Object.assign(controls.style, {
            display: "flex",
            alignItems: "center",
            gap: "6px",
            flexWrap: "wrap",
            marginBottom: "10px"
        });

        this.previousButton = this._createButton("◀", "Previous loaded frame");
        this.playButton = this._createButton("▶", "Play loaded frames");
        this.nextButton = this._createButton("▶|", "Next loaded frame");

        this.previousButton.addEventListener("click", () =>
            this.timeController.previous()
        );

        this.playButton.addEventListener("click", () =>
            this.timeController.togglePlayback()
        );

        this.nextButton.addEventListener("click", () =>
            this.timeController.next()
        );

        const backButton = this._createButton("− Step", "Step backward in time");
        const forwardButton = this._createButton("+ Step", "Step forward in time");

        backButton.addEventListener("click", () =>
            this.timeController.stepBackward()
        );

        forwardButton.addEventListener("click", () =>
            this.timeController.stepForward()
        );

        this.stepLabel = document.createElement("span");
        this.stepLabel.style.cssText =
            "font-size:11px;color:#cbd5e1;margin:0 4px";

        this.speedSelect = document.createElement("select");

        for (const speed of [0.25, 0.5, 1, 2, 4])
        {
            const option = document.createElement("option");
            option.value = String(speed);
            option.textContent = `Playback ${speed}×`;
            option.selected = speed === this.timeController.getPlaybackSpeed();
            this.speedSelect.appendChild(option);
        }

        this._styleInput(this.speedSelect);

        this.speedSelect.addEventListener("change", () =>
            this.timeController.setPlaybackSpeed(Number(this.speedSelect.value))
        );

        this.zoomSelect = document.createElement("select");

        const zoomOptions = [
            { label: "6 hours", hours: 6 },
            { label: "24 hours", hours: 24 },
            { label: "7 days", hours: 24 * 7 },
            { label: "30 days", hours: 24 * 30 },
            { label: "6 months", hours: 24 * 182.625 },
            { label: "1 year", hours: 24 * 365.2425 },
            { label: "5 years", hours: 24 * 365.2425 * 5 },
            { label: "10 years", hours: 24 * 365.2425 * 10 },
            { label: "20 years", hours: 24 * 365.2425 * 20 }
        ];

        for (const zoom of zoomOptions)
        {
            const option = document.createElement("option");
            option.value = String(zoom.hours);
            option.textContent = `View: ${zoom.label}`;
            this.zoomSelect.appendChild(option);
        }

        this.zoomSelect.value = String(24 * 30);
        this._styleInput(this.zoomSelect);

        this.zoomSelect.addEventListener("change", () =>
        {
            this.timelineHours = Number(this.zoomSelect.value);
            this._renderTimeline();
        });

        const todayButton = this._createButton("Go to reference", "Center the timeline on the reference time");

        todayButton.addEventListener("click", () =>
        {
            this.timeController.setSelectedTime(
                this.timeController.getReferenceTime()
            );
        });

        controls.append(
            this.previousButton,
            this.playButton,
            this.nextButton,
            backButton,
            forwardButton,
            this.stepLabel,
            this.speedSelect,
            this.zoomSelect,
            todayButton
        );

        // Unified timeline track
        this.timelineViewport = document.createElement("div");

        Object.assign(this.timelineViewport.style, {
            position: "relative",
            height: "100px",
            overflow: "hidden",
            border: "1px solid rgba(255,255,255,0.14)",
            borderRadius: "8px",
            background: "rgba(255,255,255,0.035)",
            cursor: "grab",
            touchAction: "pan-y"
        });

        this.timelineContent = document.createElement("div");

        Object.assign(this.timelineContent.style, {
            position: "absolute",
            inset: "0"
        });

        this.coverage = document.createElement("div");

        Object.assign(this.coverage.style, {
            position: "absolute",
            top: "37px",
            height: "14px",
            background: "rgba(34,197,94,0.2)",
            borderTop: "1px solid rgba(74,222,128,0.8)",
            borderBottom: "1px solid rgba(74,222,128,0.8)",
            pointerEvents: "none"
        });

        this.ticks = document.createElement("div");

        Object.assign(this.ticks.style, {
            position: "absolute",
            inset: "0",
            pointerEvents: "none"
        });

        this.referenceMarker = this._createMarker("#22c55e", "REF");
        this.selectedMarker = this._createMarker("#60a5fa", "SELECTED");

        this.timelineContent.append(
            this.coverage,
            this.ticks,
            this.referenceMarker,
            this.selectedMarker
        );

        this.timelineViewport.appendChild(this.timelineContent);

        // Dragging pans through time and updates the selected time.
        this.timelineViewport.addEventListener("pointerdown", event =>
        {
            if (event.button !== 0) return;

            this.isDragging = true;
            this.dragStartX = event.clientX;
            this.dragStartTime = this.timeController.getSelectedTime().getTime();

            this.timelineViewport.setPointerCapture(event.pointerId);
            this.timelineViewport.style.cursor = "grabbing";
        });

        this.timelineViewport.addEventListener("pointermove", event =>
        {
            if (!this.isDragging) return;

            const width = Math.max(1, this.timelineViewport.clientWidth);
            const deltaPixels = event.clientX - this.dragStartX;

            // Drag right to move toward earlier times; drag left to move forward.
            const deltaTime =
                -(deltaPixels / width) * this.timelineHours * 3600000;

            this.timeController.setSelectedTime(
                new Date(this.dragStartTime + deltaTime)
            );
        });

        const endDrag = () =>
        {
            this.isDragging = false;
            this.timelineViewport.style.cursor = "grab";
        };

        this.timelineViewport.addEventListener("pointerup", endDrag);
        this.timelineViewport.addEventListener("pointercancel", endDrag);
        this.timelineViewport.addEventListener("lostpointercapture", endDrag);

        // Wheel zooms; ordinary pointer dragging pans.
        this.timelineViewport.addEventListener("wheel", event =>
        {
            const currentIndex = [...this.zoomSelect.options].findIndex(
                option => Number(option.value) === this.timelineHours
            );

            let nextIndex = currentIndex;

            if (event.deltaY < 0) nextIndex--;
            else nextIndex++;

            nextIndex = Math.max(
                0,
                Math.min(this.zoomSelect.options.length - 1, nextIndex)
            );

            if (nextIndex === currentIndex) return;

            event.preventDefault();

            this.zoomSelect.selectedIndex = nextIndex;
            this.timelineHours = Number(this.zoomSelect.value);
            this._renderTimeline();
        }, { passive: false });

        this.statusLabel = document.createElement("div");

        Object.assign(this.statusLabel.style, {
            marginTop: "8px",
            fontSize: "11px",
            color: "#cbd5e1"
        });

        this.panel.append(header, dateRow, controls, this.timelineViewport, this.statusLabel);
        document.body.appendChild(this.panel);

        this._renderTimeline();
    }

    // --------------------------------------------------
    // UI helpers
    // --------------------------------------------------

    _createField(labelText, input)
    {
        const label = document.createElement("label");

        Object.assign(label.style, {
            display: "flex",
            flexDirection: "column",
            gap: "4px",
            fontSize: "11px",
            color: "#94a3b8"
        });

        label.append(labelText, input);
        return label;
    }

    _createDateInput()
    {
        const input = document.createElement("input");
        input.type = "datetime-local";
        this._styleInput(input);
        input.style.width = "205px";
        return input;
    }

    _styleInput(input)
    {
        Object.assign(input.style, {
            boxSizing: "border-box",
            height: "30px",
            padding: "4px 7px",
            border: "1px solid rgba(255,255,255,0.2)",
            borderRadius: "5px",
            background: "#111827",
            color: "#f8fafc",
            fontSize: "12px"
        });
    }

    _createButton(text, title)
    {
        const button = document.createElement("button");
        button.textContent = text;
        button.title = title;

        Object.assign(button.style, {
            height: "30px",
            padding: "0 9px",
            border: "1px solid rgba(255,255,255,0.2)",
            borderRadius: "5px",
            background: "rgba(255,255,255,0.08)",
            color: "#f8fafc",
            fontSize: "12px",
            cursor: "pointer"
        });

        button.addEventListener("mouseenter", () =>
            button.style.background = "rgba(255,255,255,0.18)"
        );

        button.addEventListener("mouseleave", () =>
            button.style.background = "rgba(255,255,255,0.08)"
        );

        return button;
    }

    _createMarker(color, labelText)
    {
        const marker = document.createElement("div");

        Object.assign(marker.style, {
            position: "absolute",
            top: "0",
            bottom: "0",
            width: "2px",
            background: color,
            zIndex: labelText === "SELECTED" ? "4" : "3",
            pointerEvents: "none"
        });

        const label = document.createElement("span");
        label.textContent = labelText;

        Object.assign(label.style, {
            position: "absolute",
            top: "5px",
            left: "5px",
            color,
            fontSize: "9px",
            fontWeight: "700",
            whiteSpace: "nowrap"
        });

        marker.appendChild(label);
        return marker;
    }

    // --------------------------------------------------
    // Unified timeline rendering
    // --------------------------------------------------

    _renderTimeline()
    {
        if (!this.timelineViewport || !this.timelineContent) return;

        const width = Math.max(1, this.timelineViewport.clientWidth);
        this.lastWidth = width;

        const selected = this.timeController.getSelectedTime().getTime();
        const reference = this.timeController.getReferenceTime().getTime();

        // The visible range follows the selected time. No fixed end date.
        this.rangeStart = selected - this.timelineHours * 3600000 / 2;
        this.rangeEnd = selected + this.timelineHours * 3600000 / 2;

        this.timelineContent.style.width = `${width}px`;
        this.ticks.replaceChildren();

        const tickStep = this._tickInterval(this.timelineHours);
        const start = this.rangeStart;
        const end = this.rangeEnd;

        let tick = Math.floor(start / tickStep) * tickStep;
        let guard = 0;

        while (tick <= end && guard < 1000)
        {
            const x = ((tick - start) / (end - start)) * width;
            const date = new Date(tick);
            const major = this._isMajorTick(date, this.timelineHours);

            const line = document.createElement("div");

            Object.assign(line.style, {
                position: "absolute",
                left: `${x}px`,
                top: major ? "24px" : "34px",
                height: major ? "34px" : "14px",
                borderLeft: `1px solid ${major ? "#64748b" : "#334155"}`
            });

            this.ticks.appendChild(line);

            if (major)
            {
                const label = document.createElement("span");
                label.textContent = this._formatTick(date, this.timelineHours);

                Object.assign(label.style, {
                    position: "absolute",
                    left: `${Math.min(x + 4, width - 110)}px`,
                    top: "9px",
                    color: "#cbd5e1",
                    fontSize: "10px",
                    whiteSpace: "nowrap"
                });

                this.ticks.appendChild(label);
            }

            tick += tickStep;
            guard++;
        }

        this._renderCoverage();

        this.referenceMarker.style.display =
            reference >= start && reference <= end ? "block" : "none";

        if (this.referenceMarker.style.display !== "none")
        {
            this.referenceMarker.style.left =
                `${((reference - start) / (end - start)) * width}px`;
        }

        // Selected time is centered by design.
        this.selectedMarker.style.left = `${width / 2}px`;
    }

    _tickInterval(spanHours)
    {
        if (spanHours <= 12) return 60 * 60 * 1000;
        if (spanHours <= 48) return 3 * 60 * 60 * 1000;
        if (spanHours <= 24 * 14) return 12 * 60 * 60 * 1000;
        if (spanHours <= 24 * 60) return 24 * 60 * 60 * 1000;
        if (spanHours <= 24 * 180) return 7 * 24 * 60 * 60 * 1000;
        if (spanHours <= 24 * 730) return 30 * 24 * 60 * 60 * 1000;
        return 365.2425 * 24 * 60 * 60 * 1000;
    }

    _isMajorTick(date, spanHours)
    {
        if (spanHours <= 48) return date.getUTCHours() % 6 === 0;
        if (spanHours <= 24 * 14) return date.getUTCHours() === 0;
        if (spanHours <= 24 * 180) return date.getUTCHours() === 0;
        if (spanHours <= 24 * 730) return date.getUTCDate() <= 7;
        return date.getUTCMonth() === 0;
    }

    _formatTick(date, spanHours)
    {
        if (spanHours <= 48)
        {
            return date.toISOString().slice(5, 16).replace("T", " ");
        }

        if (spanHours <= 24 * 180)
        {
            return date.toISOString().slice(0, 10);
        }

        if (spanHours <= 24 * 730)
        {
            return date.toISOString().slice(0, 7);
        }

        return String(date.getUTCFullYear());
    }

    _renderCoverage()
    {
        if (this.datasetStart === null || this.datasetEnd === null)
        {
            this.coverage.style.display = "none";
            return;
        }

        const start = Math.max(this.datasetStart, this.rangeStart);
        const end = Math.min(this.datasetEnd, this.rangeEnd);

        if (end <= start)
        {
            this.coverage.style.display = "none";
            return;
        }

        const width = this.timelineViewport.clientWidth;
        const span = this.rangeEnd - this.rangeStart;

        this.coverage.style.display = "block";
        this.coverage.style.left = `${((start - this.rangeStart) / span) * width}px`;
        this.coverage.style.width = `${((end - start) / span) * width}px`;
    }

    setDatasetRange(start, end)
    {
        const a = this._timestamp(start);
        const b = this._timestamp(end);

        if (b <= a)
        {
            throw new Error("Dataset end must be after dataset start.");
        }

        this.datasetStart = a;
        this.datasetEnd = b;
        this._renderCoverage();
    }

    // --------------------------------------------------
    // State synchronization
    // --------------------------------------------------

    _getCurrentState()
    {
        return {
            index: this.timeController.getCurrentIndex(),
            time: this.timeController.getCurrentTime(),
            frame: this.timeController.getCurrentFrame(),
            frameCount: this.timeController.getFrameCount(),
            playing: this.timeController.isPlaying(),
            referenceTime: this.timeController.getReferenceTime(),
            selectedTime: this.timeController.getSelectedTime(),
            timeOffset: this.timeController.getTimeOffset(),
            stepSeconds: this.timeController.getStepSeconds()
        };
    }

    _update(state)
    {
        if (!this.panel) return;

        const selected = this._timestamp(state.selectedTime);
        const reference = this._timestamp(state.referenceTime);

        this.referenceInput.value = this._toInputValue(reference);
        this.selectedInput.value = this._toInputValue(selected);

        this.currentTimeLabel.textContent =
            `Selected: ${new Date(selected).toISOString().replace("T", " ").slice(0, 19)} UTC`;

        const offsetHours = state.timeOffset / 3600;
        const sign = offsetHours > 0 ? "+" : "";

        this.offsetLabel.textContent =
            `${sign}${offsetHours.toLocaleString(undefined, { maximumFractionDigits: 2 })} h from reference`;

        this.stepLabel.textContent =
            `Step: ${this._formatDuration(state.stepSeconds)}`;

        this.playButton.textContent = state.playing ? "❚❚" : "▶";
        this.playButton.title = state.playing ? "Pause playback" : "Play loaded frames";

        const hasExactFrame = state.frame &&
            this._timestamp(state.frame.time) === selected;

        if (hasExactFrame)
        {
            this.statusLabel.textContent =
                `Weather frame available · ${state.frameCount} loaded frame(s)`;
            this.statusLabel.style.color = "#86efac";
        }
        else
        {
            this.statusLabel.textContent =
                `No exact weather frame loaded for this selected time · ${state.frameCount} loaded frame(s)`;
            this.statusLabel.style.color = "#fbbf24";
        }

        // Recenter the time window when selection changes.
        // During a drag, the range follows the moving selected time.
        this._renderTimeline();
    }

    // --------------------------------------------------
    // Date helpers
    // --------------------------------------------------

    _timestamp(value)
    {
        const timestamp = value instanceof Date
            ? value.getTime()
            : new Date(value).getTime();

        if (!Number.isFinite(timestamp))
        {
            throw new Error(`Invalid timestamp: ${value}`);
        }

        return timestamp;
    }

    _parseInput(value)
    {
        // datetime-local has no timezone. Treat its displayed value as UTC.
        const date = new Date(`${value}:00Z`);
        return Number.isFinite(date.getTime()) ? date : null;
    }

    _toInputValue(value)
    {
        const date = new Date(value);
        const pad = number => String(number).padStart(2, "0");

        return (
            `${date.getUTCFullYear()}-` +
            `${pad(date.getUTCMonth() + 1)}-` +
            `${pad(date.getUTCDate())}T` +
            `${pad(date.getUTCHours())}:` +
            `${pad(date.getUTCMinutes())}`
        );
    }

    _formatDuration(seconds)
    {
        if (seconds % 86400 === 0) return `${seconds / 86400} day(s)`;
        if (seconds % 3600 === 0) return `${seconds / 3600} hour(s)`;
        if (seconds % 60 === 0) return `${seconds / 60} minute(s)`;
        return `${seconds} second(s)`;
    }

    destroy()
    {
        if (this._listener)
        {
            this.timeController.removeListener(this._listener);
            this._listener = null;
        }

        if (this._resizeHandler)
        {
            window.removeEventListener("resize", this._resizeHandler);
            this._resizeHandler = null;
        }

        this.panel?.remove();
        this.panel = null;
    }
}
