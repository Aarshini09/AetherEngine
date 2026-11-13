import time


class ApplicationLoop:
    """
    Controls the lifetime of the Avani application.

    The loop owns the application's update cycle but does not
    contain weather, anomaly, visualization, or AI logic.

    Those responsibilities belong to their respective systems.
    """

    def __init__(self, application, tick_rate=20.0):
        self.application = application

        if tick_rate <= 0.0:
            raise ValueError("tick_rate must be greater than zero.")

        self.tick_rate = float(tick_rate)
        self.tick_interval = 1.0 / self.tick_rate

        self._running = False

        self._tick_count = 0
        self._status_timer = 0.0
        self._status_interval = 1.0

    @property
    def running(self):
        return self._running

    @property
    def tick_count(self):
        return self._tick_count

    def run(self):
        """
        Run the Avani application until the application requests
        shutdown.
        """

        if self._running:
            raise RuntimeError("Application loop is already running.")

        self._running = True

        previous_time = time.perf_counter()

        print("[Avani] Runtime started.")
        print(
            f"[Avani] Tick rate: {self.tick_rate:.1f} Hz"
        )
        print()

        try:
            while self._running and not self.application.should_close():
                current_time = time.perf_counter()

                delta_time = current_time - previous_time
                previous_time = current_time

                self._tick_count += 1
                self._status_timer += delta_time

                self.application.update(delta_time)

                if self._status_timer >= self._status_interval:
                    self._print_status(delta_time)
                    self._status_timer = 0.0

                elapsed = time.perf_counter() - current_time
                remaining = self.tick_interval - elapsed

                if remaining > 0.0:
                    time.sleep(remaining)

        finally:
            self._running = False

            print()
            print("[Avani] Runtime stopped.")

    def _print_status(self, delta_time):
        """
        Print a low-frequency runtime status message.

        The application may update many times per second, but the
        console only receives one status message per second.
        """

        if delta_time <= 0.0:
            actual_rate = 0.0
        else:
            actual_rate = 1.0 / delta_time

        print(
            f"[Avani] Runtime alive | "
            f"Ticks: {self._tick_count} | "
            f"Application update: {actual_rate:.1f} Hz"
        )

    def stop(self):
        """
        Request the application loop to stop.
        """

        self._running = False