class MediaFilter:
    def __init__(
            self, 
            albums: tuple[str, ...], 
            title: str,
            location: str,
            people: str,
            people_count_range: tuple[int, int],
            file_type: int,
            file_ext: str,
            tags: str,
            date_range: tuple[str, str],
            days: str,
            months: str,
            years: str,
            days_of_week: str,
            sort: tuple[int, int]):

        self.albums = albums
        self.title = title
        self.location = location
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
        
