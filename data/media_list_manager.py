import pickle
from ops import file_ops


class MediaListManager:
    def __init__(self):
        self.media_lists_dict = {}  # {list_name: [uuids]}
        self.load_media_lists_file()

    def load_media_lists_file(self):
        if file_ops.check_file_exists("res/database/", "media_lists.pkl"):
            with open("res/database/media_lists.pkl", "rb") as f:
                self.media_lists_dict = pickle.load(f)

    def save_media_lists_file(self):
        with open("res/database/media_lists.pkl", "wb") as f:
            pickle.dump(self.media_lists_dict, f)

    def create_media_list(self, list_name: str, uuids: list[str]):
        self.media_lists_dict[list_name] = list(dict.fromkeys(uuids))
        self.save_media_lists_file()

    def edit_media_list(self, old_name: str, new_name: str, uuids: list[str]):
        if old_name in self.media_lists_dict.keys():
            self.media_lists_dict[new_name] = list(dict.fromkeys(uuids))
            del self.media_lists_dict[old_name]
            self.save_media_lists_file()

    def rename_media_list(self, old_name: str, new_name: str):
        if old_name in self.media_lists_dict.keys():
            self.media_lists_dict[new_name] = self.media_lists_dict.pop(old_name)
            self.save_media_lists_file()

    def delete_media_list(self, list_name: str):
        if list_name in self.media_lists_dict.keys():
            del self.media_lists_dict[list_name]
            self.save_media_lists_file()

    def add_uuids_to_media_list(self, list_name: str, uuids: list[str]):
        if list_name not in self.media_lists_dict.keys():
            self.create_media_list(list_name, uuids)
        else:
            current_uuids = self.media_lists_dict[list_name].copy()
            current_uuids.extend(list(dict.fromkeys(uuids)))
            self.media_lists_dict[list_name] = list(dict.fromkeys(current_uuids))
        self.save_media_lists_file()

    def remove_uuids_from_media_list(self, list_name: str, uuids: list[str]):
        if list_name in self.media_lists_dict.keys():
            self.media_lists_dict[list_name] = [
                uuid for uuid in self.media_lists_dict[list_name] if uuid not in uuids
            ]
            self.save_media_lists_file()

    def get_media_list_names(self) -> list:
        return list(self.media_lists_dict.keys())

    def get_uuids_from_list(self, list_name: str) -> list:
        if list_name in self.media_lists_dict.keys():
            return self.media_lists_dict[list_name].copy()
        else:
            return []
