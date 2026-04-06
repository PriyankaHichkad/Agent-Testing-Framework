import json

def load_test_cases(file_path="data/test_cases.json"):
    with open(file_path, "r") as f:
        return json.load(f)