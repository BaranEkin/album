from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.Media import Media


class DataManager:
    def __init__(self):
        self.engine_local = create_engine("sqlite:///res/database/album.db")
        self.engine_cloud = create_engine("sqlite:///res/database/album_cloud.db")

    def get_all_media(self):
        session = sessionmaker(bind=self.engine_local)()
        try:
            # Query the Media table, ordering by the 'date' column
            media_list = session.query(Media).order_by(Media.date).all()
            return media_list
        finally:
            session.close()


if __name__ == "__main__":
    dm = DataManager()
    dm.engine_local = create_engine("sqlite:///D:/Work/self/github/album-2/res/database/album.db")
    data = dm.get_all_media()
    print(data)
