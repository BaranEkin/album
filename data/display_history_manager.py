import json
import pickle
from datetime import datetime
from data.data_manager import DataManager, MediaUUID
from ops import file_ops
from logger import log


DISPLAY_HISTORY_DIR = "res/database/"
DISPLAY_HISTORY_JSON_FILE = "display_history.json"
DISPLAY_HISTORY_PICKLE_FILE = "display_history.pkl"


class DisplayHistoryManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager: DataManager = data_manager
        self.display_history: dict[MediaUUID, datetime] = {}
        self.init_display_history()
        self.load_display_history_file()

    def init_display_history(self):
        uuids = self.data_manager.get_list_uuids()
        old_date = datetime(1900, 1, 1)
        self.display_history = {uuid: old_date for uuid in uuids}

    def load_display_history_file(self):
        try:
            if file_ops.check_file_exists(
                DISPLAY_HISTORY_DIR, DISPLAY_HISTORY_JSON_FILE
            ):
                with open(
                    f"{DISPLAY_HISTORY_DIR}{DISPLAY_HISTORY_JSON_FILE}",
                    "r",
                    encoding="utf-8",
                ) as f:
                    display_history_json = json.load(f)

                for uuid, timestamp in display_history_json.items():
                    if uuid in self.display_history:
                        self.display_history[uuid] = datetime.fromisoformat(timestamp)
            elif file_ops.check_file_exists(
                DISPLAY_HISTORY_DIR, DISPLAY_HISTORY_PICKLE_FILE
            ):
                with open(
                    f"{DISPLAY_HISTORY_DIR}{DISPLAY_HISTORY_PICKLE_FILE}", "rb"
                ) as f:
                    display_history_old = pickle.load(f)

                # Update display history with the old one
                for uuid, timestamp in display_history_old.items():
                    if uuid in self.display_history:
                        self.display_history[uuid] = timestamp

                self.save_display_history_file()
        except Exception as e:
            log(
                "DisplayHistoryManager.load_display_history_file",
                f"Failed to load display history file: {e}",
                level="error",
            )

    def save_display_history_file(self):
        with open(
            f"{DISPLAY_HISTORY_DIR}{DISPLAY_HISTORY_JSON_FILE}", "w", encoding="utf-8"
        ) as f:
            display_history_json = {
                uuid: timestamp.isoformat()
                for uuid, timestamp in self.display_history.items()
            }
            json.dump(display_history_json, f, ensure_ascii=False, indent=4)

    def update(self, uuid: MediaUUID):
        self.display_history[uuid] = datetime.now()

    def get_ordered_uuids(self) -> list[MediaUUID]:
        """Return media UUIDs ordered by the last display time. Oldest first."""
        return sorted(
            self.display_history.keys(), key=lambda x: self.display_history[x]
        )
