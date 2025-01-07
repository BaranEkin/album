import pickle
from datetime import datetime
from data.data_manager import DataManager
from ops import file_ops

class DisplayHistoryManager:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.display_history = {} # {uuid: datetime}
        self.init_display_history()
        self.load_display_history_file()
    
    def init_display_history(self):
        uuids = self.data_manager.get_list_uuids()
        self.display_history = {uuid: datetime.now() for uuid in uuids}

    def load_display_history_file(self):
        if file_ops.check_file_exists("res/database/", "display_history.pkl"):
            with open("res/database/display_history.pkl", "rb") as f:
                display_history_old = pickle.load(f)

            # Update display history with the old one
            for uuid in display_history_old.keys():
                self.display_history[uuid] = display_history_old[uuid]

    def save_display_history_file(self):
        with open("res/database/display_history.pkl", "wb") as f:
            pickle.dump(self.display_history, f)

    def update(self, uuid: str):
        self.display_history[uuid] = datetime.now()

    def get_ordered_uuids(self) -> list:
        """Return media UUIDs ordered by the last display time. Oldest first."""
        return sorted(self.display_history.keys(), key=lambda x: self.display_history[x])
    
