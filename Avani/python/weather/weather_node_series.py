class WeatherNodeSeries:
    """
    Represents the weather history of one spatial
    weather-grid node.

    The node itself represents WHERE.
    Each temporal entry represents WHEN and WHAT
    the weather was doing at that location.
    """

    def __init__(self, node):
        self.node = node
        self.states = {}

    def add_state(self, time, state):
        """
        Associate a weather state with a timestamp.
        """

        self.states[str(time)] = state

    def get_state(self, time):
        """
        Return the weather state for a timestamp.
        """

        time_key = str(time)

        if time_key not in self.states:
            raise KeyError(
                f"No weather state found for time: {time}"
            )

        return self.states[time_key]

    def get_times(self):
        """
        Return all timestamps stored for this node.
        """

        return list(self.states.keys())

    def __len__(self):
        """
        Return the number of stored timestamps.
        """

        return len(self.states)