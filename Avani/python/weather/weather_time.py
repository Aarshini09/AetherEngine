class WeatherTime:
    """
    Represents a timestamp within the weather dataset.
    """

    def __init__(self, value, index=None):
        self.value = value
        self.index = index

    def __repr__(self):
        return (
            f"WeatherTime("
            f"value={self.value}, "
            f"index={self.index}"
            f")"
        )