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
            file_type: int = 0,
            file_ext: str = "",
            tags: str = "",
            date_range: tuple[str, str] = ("", ""),
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
        self.file_type = file_type
        self.file_ext = file_ext
        self.tags = tags
        self.date_range = date_range
        self.days = days
        self.months = months
        self.years = years
        self.days_of_week = days_of_week
        self.sort = sort

    def __str__(self):
        # Return a single-line string of the instance's attributes as a dictionary
        return str(self.__dict__)
