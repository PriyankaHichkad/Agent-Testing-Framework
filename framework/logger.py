import json
from datetime import datetime
import os

class Logger:
    def __init__(self, file_path=os.path.join(os.path.dirname(__file__), "evaluation/logs.jsonl")):
        self.file_path = file_path

    def log(self, data):
        # convert datetime
        data["timestamp"] = datetime.now().isoformat()

        # FIX: convert non-serializable types
        serializable_data = self._make_serializable(data)

        with open(self.file_path, "a") as f:
            f.write(json.dumps(serializable_data) + "\n")

    def _make_serializable(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(i) for i in obj]
        else:
            return obj