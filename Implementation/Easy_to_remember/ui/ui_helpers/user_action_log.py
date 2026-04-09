# This class is for the the functionality of logging the users actions

import json
from datetime import datetime

class UserActionLog:
    def __init__(self, path="user_actions.json"):
        self.path = path

    def save(self, actions_type, value, mode_name):
        record = {
            "time": datetime.now().isoformat(),
            "action": actions_type,
            "value": value,
            "mode": mode_name,
        }

        try:
            with open("user_actions.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Could not save users action: {e}")
