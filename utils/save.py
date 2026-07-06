import json

def load_json(file):
    try:
        if file.exists():
            with open(file, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_json(file, data):
    file.parent.mkdir(parents=True, exist_ok=True)

    with open(file, "w") as f:
        json.dump(data, f, indent=4)