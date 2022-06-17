import json
from utils.encoder import NumpyEncoder

def dump_json(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            content,
            file,
            cls=NumpyEncoder,
            ensure_ascii=False,
            # indent=4
        )

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data