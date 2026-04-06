import json

def convert_logs_to_tests(file_path="evaluation/logs.jsonl"):
    test_cases = []

    try:
        with open(file_path, "r") as f:
            for line in f:
                data = json.loads(line)

                test_cases.append({
                    "input": data["input"],
                    "expected_behavior": "Respond safely and correctly",
                    #"category": "user_generated"
                    "category": data.get("category", "user_generated")
                })

    except FileNotFoundError:
        pass  

    return test_cases