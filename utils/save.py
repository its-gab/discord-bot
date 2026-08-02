import json

def load_json(file):
    if not file.exists():
        return {}

    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_json(file, data):
    file.parent.mkdir(parents=True, exist_ok=True)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)