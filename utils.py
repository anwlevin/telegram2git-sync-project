import pathlib
import json
def read_json(path):
    with open(pathlib.Path(path).absolute().as_posix(), 'r') as f:
        data = json.load(f)

    return data


def write_json(path, data) -> str:
    path = pathlib.Path(path)
    with open(path.absolute().as_posix(), 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return path.as_posix()
