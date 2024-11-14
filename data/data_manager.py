import re
import uuid
from typing import Sequence, Literal
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, or_, select

from logger import log
from config.config import Config
from data.orm import Album, Media
from data.media_filter import MediaFilter
from data.helpers import date_to_julian, current_time_in_unix_subsec, normalize_date, date_includes
from ops import cloud_ops, file_ops


class DataManager:
    def __init__(self):
        self.db_engine = None

    def init_db_engine(self):
        self.db_engine = create_engine(f"sqlite:///{Config.DATABASE_DIR}/album.db")

    def get_db_engine(self):
        if not self.db_engine:
            self.init_db_engine()
        return self.db_engine

    @contextmanager
    def get_session(self):
        session = sessionmaker(bind=self.get_db_engine())()
        try:
            yield session
        finally:
            session.close()
            self.db_engine.dispose()
            self.db_engine = None

    def build_media(
            self,
            path,
            topic,
            title,
            location,
            date_text,
            date_est,
            albums,
            tags,
            notes,
            people,
            people_detect,
            people_count,
            private
    ) -> Media:
        date = date_to_julian(date_text)
        created_at = current_time_in_unix_subsec()

        # UUID/GUID (Universally/Globally Unique Identifier) using UUID-4 Standard (Random)
        media_uuid = str(uuid.uuid4().hex)
        file_ops.add_media(media_uuid=media_uuid, media_path=path)

        media = Media()
        media.media_uuid = media_uuid
        media.created_at = created_at
        media.modified_at = created_at
        media.topic = topic
        media.title = title
        media.location = location
        media.date = date
        media.date_text = date_text
        media.date_est = date_est
        media.rank = self.get_last_rank(date) + 1.0
        media.tags = tags
        media.notes = notes
        media.albums = albums
        media.people = people
        media.people_detect = people_detect
        media.people_count = people_count
        media.extension = file_ops.get_file_extension(path)
        media.type = file_ops.get_file_type(path)
        media.private = private

        return media

    def get_all_media(self) -> Sequence[Media]:
        with self.get_session() as session:
            # Query the Media table, ordering by the 'date' column
            media_list = session.execute(select(Media).order_by(Media.date, Media.rank)).scalars().all()
            return media_list


    def get_list_people(self) -> list[str]:
        media_list = self.get_all_media()
        list_people = []
        for media in media_list:
            if media.people is not None:
                people = media.people.split(",")
                if people[0] != "":
                    for person in people:
                        if person not in list_people:
                            list_people.append(person)

        return sorted(list_people)
    
    def get_media_of_date(self, date: float) -> Sequence[Media]:
        with self.get_session() as session:
            media_list = session.execute(select(Media).where(Media.date == date).order_by(Media.rank)).scalars().all()
            return media_list


    def get_last_rank(self, date: float):
        media_list = self.get_media_of_date(date)
        last_rank = max([media.rank for media in media_list])
        return last_rank

    def get_all_albums(self) -> Sequence[Album]:
        with self.get_session() as session:
            album_list = session.execute(select(Album)).scalars().all()
            return album_list

    def get_all_album_paths_with_tags(self) -> list[tuple[str, str]]:
        album_list = self.get_all_albums()

        if album_list:
            # Create a mapping from tags to nodes for easy access
            tag_to_album = {item.tag: item for item in album_list}

            # Create a list to store all paths with tags
            paths = []

            def build_path(album):
                path_elements = []
                current_album = album

                # Traverse up to the root node, building the path
                while current_album:
                    path_elements.insert(0, current_album.name)  # Insert at the beginning to reverse the order
                    # Find the parent tag by truncating the current node's path
                    parent_path = current_album.path[:-len(current_album.tag)]
                    parent_tag = parent_path[-3:] if parent_path else None
                    current_album = tag_to_album.get(parent_tag)

                # Join the path elements to form the full path
                return "/".join(path_elements)

            # Generate paths for all nodes in the data
            for album in album_list:
                full_path = build_path(album)
                paths.append((full_path, album.tag))

            return sorted(paths, key=lambda x: x[0])

    def update_local_db(self) -> bool:
        return cloud_ops.download_from_s3_bucket("album_cloud.db", f"{Config.DATABASE_DIR}/album.db")
    
        
    def insert_media_list_to_local(self, media_list: list[Media]):
        with self.get_session() as session:
            user_name = cloud_ops.get_user_name()
            for media in media_list:
                media.user_name = user_name
                session.add(media)
            session.commit()

    def get_filtered_media(self, media_filter: MediaFilter) -> list[Media]:

        with self.get_session() as session:
            # Query the Media table, ordering by the 'date' column
            media_list = session.execute(DataManager._build_selection(media_filter)).scalars().all()

            if media_list:
                if media_filter.days:
                    media_list = DataManager._apply_date_filter(media_list, media_filter.days, mode="day")
                if media_filter.months:
                    media_list = DataManager._apply_date_filter(media_list, media_filter.months, mode="month")
                if media_filter.years:
                    media_list = DataManager._apply_date_filter(media_list, media_filter.years, mode="year")
                if media_filter.days_of_week:
                    media_list = DataManager._apply_date_filter(media_list, media_filter.days_of_week, mode="weekday")
            
            if len(media_list) == 0:
                log("DataManager.get_filtered_media", f"Filter returned no results. Used Filter: {media_filter}", level="warning")
            else:
                log("DataManager.get_filtered_media", f"Filter returned {len(media_list)} results. Used Filter: {media_filter}")

            return media_list

    @staticmethod
    def _build_selection(media_filter: MediaFilter):
        selection = select(Media)

        if media_filter.albums[0]:
            selection = selection.where(or_(*[Media.albums.contains(album) for album in media_filter.albums]))

        if media_filter.quick:
            quick_filter_fields = [
                Media.topic,
                Media.title,
                Media.location,
                Media.people,
                Media.tags,
                Media.extension,
                Media.date_text
            ]
            
            selection = selection.where(
                or_(*[field.like(f"%{media_filter.quick}%") for field in quick_filter_fields])
            )
            selection = selection.order_by(Media.date, Media.rank)
            return selection

        if media_filter.topic:
            filter_condition = DataManager._build_filter_condition(
                media_filter.topic,
                "search_topic"
            )
            selection = selection.where(filter_condition)

        if media_filter.title:
            filter_condition = DataManager._build_filter_condition(
                media_filter.title,
                "search_title"
            )
            selection = selection.where(filter_condition)

        if media_filter.location:
            filter_condition = DataManager._build_filter_condition(
                media_filter.location,
                "search_location"
            )
            selection = selection.where(filter_condition)

        if media_filter.people:
            filter_condition = DataManager._build_filter_condition(
                media_filter.people,
                "search_people"
            )
            selection = selection.where(filter_condition)

        if media_filter.tags:
            filter_condition = DataManager._build_filter_condition(
                media_filter.tags,
                "search_tags"
            )
            selection = selection.where(filter_condition)

        if media_filter.location_exact:
            selection = selection.where(Media.location == media_filter.location_exact)

        if media_filter.file_ext:
            selection = selection.where(Media.extension.ilike(f"%{media_filter.file_ext}%"))

        if media_filter.date_range[0]:
            date_start = date_to_julian(normalize_date(media_filter.date_range[0]))
            if date_start:
                if media_filter.date_range[1]:
                    date_end = date_to_julian(normalize_date(media_filter.date_range[1]))
                    if date_end:
                        selection = selection.where(Media.date >= date_start, Media.date <= date_end)
                else:
                    selection = selection.where(Media.date == date_start)

        if media_filter.people_count_range[0] != -1:
            count_min = media_filter.people_count_range[0]
            if media_filter.people_count_range[1] != -1:
                count_max = media_filter.people_count_range[1]
                selection = selection.where(Media.people_count >= count_min, Media.people_count <= count_max)
            else:
                selection = selection.where(Media.people_count == count_min)

        if media_filter.sort:
            column_mapping = {
                0: Media.date,
                1: Media.title,
                2: Media.location,
                3: Media.type,
                4: Media.people,
                5: Media.extension
            }
            selection = selection.order_by(column_mapping[media_filter.sort[0]], column_mapping[media_filter.sort[1]], Media.rank)

        return selection

    @staticmethod
    def _build_select_people(filter_string: str):
        filter_condition = DataManager._build_filter_condition(filter_string, "search_people")
        return select(Media).where(filter_condition)

    @staticmethod
    def _apply_date_filter(result: Sequence[Media], days: str, mode: Literal["day", "month", "year", "weekday"]):
        filtered_results = [media for media in result if
                            date_includes(media.date_text, media.date_est, days.split(","), mode=mode)]
        return filtered_results

    @staticmethod
    def _parse_filter_string(expr: str, function_name: str):

        def search_people(key: str):
            return Media.people.op('GLOB')(f'*{key}*')

        def search_tags(key: str):
            return Media.tags.op('GLOB')(f'*{key}*')
        
        def search_topic(key: str):
            return Media.topic.op('GLOB')(f'*{key}*')

        def search_title(key: str):
            return Media.title.op('GLOB')(f'*{key}*')

        def search_location(key: str):
            return Media.location.op('GLOB')(f'*{key}*')

        # Handle + (AND) operator first (higher precedence)
        open_parens = 0
        for i, char in enumerate(expr):
            if char == '[':
                open_parens += 1
            elif char == ']':
                open_parens -= 1
            # Only split by + (AND) when not inside parentheses
            elif open_parens == 0 and char == '+':
                parts = expr.split('+', 1)
                return and_(
                    DataManager._parse_filter_string(parts[0].replace("[", "").replace("]", ""), function_name),
                    DataManager._parse_filter_string(parts[1].replace("[", "").replace("]", ""), function_name))

        # Handle , (OR) operator second (lower precedence)
        open_parens = 0
        for i, char in enumerate(expr):
            if char == '[':
                open_parens += 1
            elif char == ']':
                open_parens -= 1
            # Only split by , (OR) when not inside parentheses
            elif open_parens == 0 and char == ',':
                parts = expr.split(',', 1)
                return or_(
                    DataManager._parse_filter_string(parts[0].replace("[", "").replace("]", ""), function_name),
                    DataManager._parse_filter_string(parts[1].replace("[", "").replace("]", ""), function_name))

        # If no AND/OR, this is a base condition
        return eval(expr, {f"{function_name}": locals().get(function_name)})

    @staticmethod
    def _build_filter_condition(filter_string: str, function_name: str):

        def preprocess_expression(expr: str) -> str:
            """Replace custom operators with Python logical operators and wrap words in quotes"""

            # Wrap all names (words) with function_name()
            expr = re.sub(r'([a-zA-ZıİğĞüÜşŞöÖçÇ_][a-zA-Z0-9ıİğĞüÜşŞöÖçÇ_ ]*)', rf'{function_name}("\1")', expr)

            return expr

        # Process the expression to replace the custom operators
        filter_string = preprocess_expression(filter_string)
        try:
            result_filter = DataManager._parse_filter_string(filter_string, function_name)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

        return result_filter
