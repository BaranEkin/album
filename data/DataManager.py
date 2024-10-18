import re
from sqlalchemy import create_engine, and_, or_, select
from sqlalchemy.orm import sessionmaker

from config.Config import Config
from data.Media import Media


class DataManager:
    def __init__(self):
        self.engine_local = create_engine(f"sqlite:///{Config.DATABASE_DIR}/album.db")
        self.engine_cloud = create_engine(f"sqlite:///{Config.DATABASE_DIR}/album_cloud.db")

    def get_all_media(self):
        session = sessionmaker(bind=self.engine_local)()
        try:
            # Query the Media table, ordering by the 'date' column
            media_list = session.execute(select(Media).order_by(Media.date)).scalars().all()
            return media_list
        finally:
            session.close()

    def get_list_people(self):
        media_list = self.get_all_media()
        list_people = []
        for media in media_list:
            people = media.people.split(",")
            if people[0] != "":
                for person in people:
                    if person not in list_people:
                        list_people.append(person)
        
        return sorted(list_people)

    def update_local_db(self):
        session_local = sessionmaker(bind=self.engine_local)()
        session_cloud = sessionmaker(bind=self.engine_cloud)()
        try:
            new_rows_to_insert = DataManager._get_new_rows_from_cloud(session_cloud, session_local)
            DataManager._insert_rows(session_local, new_rows_to_insert)
            session_local.commit()
        finally:
            session_local.close()
            session_cloud.close()

    @staticmethod
    def _get_new_rows_from_cloud(session_cloud, session_local):
        local_media_ids = session_local.query(Media.media_id).all()
        local_media_id_list = [id_tuple[0] for id_tuple in local_media_ids]
        new_rows = session_cloud.query(Media).filter(~Media.media_id.in_(local_media_id_list)).all()
        return new_rows

    @staticmethod
    def _insert_rows(session, rows):
        for row in rows:
            new_media_copy = Media(
                media_id=row.media_id,
                created_at=row.created_at,
                user_name=row.user_name,
                user_id=row.user_id,
                title=row.title,
                location=row.location,
                date=row.date,
                date_text=row.date_text,
                date_est=row.date_est,
                thumbnail_key=row.thumbnail_key,
                media_key=row.media_key,
                type=row.type,
                extension=row.extension,
                private=row.private,
                people=row.people,
                people_count=row.people_count,
                notes=row.notes,
                tags=row.tags,
                albums=row.albums
            )
            session.add(new_media_copy)

    
    def _parse_filter_string(expr: str):

        def name_in_list(name: str):
            """Search for name in Media.people using SQLite GLOB. (Partial and case-senstive.)"""

            return Media.people.op('GLOB')(f'*{name}*')
        
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
                    DataManager._parse_filter_string(parts[0].replace("[", "").replace("]", "")), 
                    DataManager._parse_filter_string(parts[1].replace("[", "").replace("]", "")))

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
                    DataManager._parse_filter_string(parts[0].replace("[", "").replace("]", "")), 
                    DataManager._parse_filter_string(parts[1].replace("[", "").replace("]", "")))
        
        # If no AND/OR, this is a base condition
        return eval(expr, {"name_in_list": name_in_list})

    @staticmethod
    def _build_people_filter_condition(filter_string: str):
        """Build SQLAlchemy filter condition for Media.people from filter string."""
        
        def preprocess_expression(expr: str) -> str:
            """Replace custom operators with Python logical operators and wrap words in quotes"""
            
            # Wrap all names (words) with name_in_list()
            expr = re.sub(r'([a-zA-ZıİğĞüÜşŞöÖçÇ_][a-zA-Z0-9ıİğĞüÜşŞöÖçÇ_ ]*)', r'name_in_list("\1")', expr)

            return expr
        
        # Process the expression to replace the custom operators
        filter_string = preprocess_expression(filter_string)
        try:
            result_filter = DataManager._parse_filter_string(filter_string)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
        
        return result_filter
    
    @staticmethod
    def _build_select_people(filter_string: str):
        filter_condition = DataManager._build_people_filter_condition(filter_string) 
        return select(Media).where(filter_condition)
    
    def filter_test(self, filter_string: str):
        session = sessionmaker(bind=self.engine_local)()
        select_people = DataManager._build_select_people(filter_string).order_by(Media.date)
        results = session.execute(select_people).scalars().all()
        return results

