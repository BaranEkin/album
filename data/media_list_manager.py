import json
import pickle

from data.data_manager import MediaUUID
from logger import log
from ops import file_ops


MEDIA_LISTS_DIR = "res/database/"
MEDIA_LISTS_JSON_FILE = "media_lists.json"
MEDIA_LISTS_PICKLE_FILE = "media_lists.pkl"

MediaListName = str
MediaListsDict = dict[MediaListName, list[MediaUUID]]


class MediaListManager:
    def __init__(self):
        self.media_lists_dict: MediaListsDict = {}
        self.load_media_lists_file()

    def load_media_lists_file(self):
        try:
            if file_ops.check_file_exists(MEDIA_LISTS_DIR, MEDIA_LISTS_JSON_FILE):
                with open(
                    f"{MEDIA_LISTS_DIR}{MEDIA_LISTS_JSON_FILE}",
                    "r",
                    encoding="utf-8",
                ) as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    self.media_lists_dict = {
                        str(name): [str(uuid) for uuid in uuids]
                        for name, uuids in data.items()
                        if isinstance(name, str) and isinstance(uuids, list)
                    }
            elif file_ops.check_file_exists(MEDIA_LISTS_DIR, MEDIA_LISTS_PICKLE_FILE):
                with open(f"{MEDIA_LISTS_DIR}{MEDIA_LISTS_PICKLE_FILE}", "rb") as f:
                    data = pickle.load(f)

                if isinstance(data, dict):
                    self.media_lists_dict = data

                self.save_media_lists_file()
        except Exception as e:
            log(
                "MediaListManager.load_media_lists_file",
                f"Failed to load media lists file: {e}",
                level="error",
            )

    def save_media_lists_file(self):
        with open(
            f"{MEDIA_LISTS_DIR}{MEDIA_LISTS_JSON_FILE}", "w", encoding="utf-8"
        ) as f:
            json.dump(self.media_lists_dict, f, ensure_ascii=False, indent=4)

    def create_media_list(self, list_name: MediaListName, uuids: list[MediaUUID]):
        self.media_lists_dict[list_name] = list(dict.fromkeys(uuids))
        self.save_media_lists_file()

    def edit_media_list(
        self,
        old_name: MediaListName,
        new_name: MediaListName,
        uuids: list[MediaUUID],
    ):
        if old_name in self.media_lists_dict.keys():
            self.media_lists_dict[new_name] = list(dict.fromkeys(uuids))
            del self.media_lists_dict[old_name]
            self.save_media_lists_file()

    def rename_media_list(self, old_name: MediaListName, new_name: MediaListName):
        if old_name in self.media_lists_dict.keys():
            self.media_lists_dict[new_name] = self.media_lists_dict.pop(old_name)
            self.save_media_lists_file()

    def delete_media_list(self, list_name: MediaListName):
        if list_name in self.media_lists_dict.keys():
            del self.media_lists_dict[list_name]
            self.save_media_lists_file()

    def add_uuids_to_media_list(self, list_name: MediaListName, uuids: list[MediaUUID]):
        if list_name not in self.media_lists_dict.keys():
            self.create_media_list(list_name, uuids)
        else:
            current_uuids = self.media_lists_dict[list_name].copy()
            current_uuids.extend(list(dict.fromkeys(uuids)))
            self.media_lists_dict[list_name] = list(dict.fromkeys(current_uuids))
        self.save_media_lists_file()

    def remove_uuids_from_media_list(
        self, list_name: MediaListName, uuids: list[MediaUUID]
    ):
        if list_name in self.media_lists_dict.keys():
            self.media_lists_dict[list_name] = [
                uuid for uuid in self.media_lists_dict[list_name] if uuid not in uuids
            ]
            self.save_media_lists_file()

    def get_media_list_names(self) -> list[MediaListName]:
        return list(self.media_lists_dict.keys())

    def get_uuids_from_list(self, list_name: MediaListName) -> list[MediaUUID]:
        if list_name in self.media_lists_dict.keys():
            return self.media_lists_dict[list_name].copy()
        else:
            return []
