class MediaFilter:
    def __init__(
            self,
            albums: tuple[str, ...] = ("",),
            quick: str = "",
            topic: str = "",
            title: str = "",
            location: str = "",
            location_exact: str = "",
            people: str = "",
            people_count_range: tuple[int, int] = (-1, -1),
            people_count_range_enabled: bool = False,
            file_type: int = 0,
            file_ext: str = "",
            tags: str = "",
            date_range: tuple[str, str] = ("", ""),
            date_range_enabled: bool = False,
            created_at_range: tuple[float, float] = (-1.0, -1.0),
            created_at_range_enabled: bool = False,
            days: str = "",
            months: str = "",
            years: str = "",
            days_of_week: str = "",
            sort: tuple[int, int] = (0, 0)):
        self.albums = albums
        self.quick = quick
        self.topic = topic
        self.title = title
        self.location = location
        self.location_exact = location_exact
        self.people = people
        self.people_count_range = people_count_range
        self.people_count_range_enabled = people_count_range_enabled
        self.file_type = file_type
        self.file_ext = file_ext
        self.tags = tags
        self.date_range = date_range
        self.date_range_enabled = date_range_enabled
        self.created_at_range = created_at_range
        self.created_at_range_enabled = created_at_range_enabled
        self.days = days
        self.months = months
        self.years = years
        self.days_of_week = days_of_week
        self.sort = sort

    def __str__(self):
        # Return a single-line string of the instance's attributes as a dictionary
        return str(self.__dict__)
