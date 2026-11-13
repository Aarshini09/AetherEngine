class WeatherVariable:
    """
    Describes how a weather variable is represented
    in the application and in the underlying data source.
    """

    def __init__(
        self,
        name,
        source_name,
        input_unit,
        output_unit,
        conversion
    ):
        self.name = name
        self.source_name = source_name
        self.input_unit = input_unit
        self.output_unit = output_unit
        self.conversion = conversion

    def convert(self, data):
        """
        Convert data from the source unit into the
        application's output unit.
        """

        return self.conversion(data)