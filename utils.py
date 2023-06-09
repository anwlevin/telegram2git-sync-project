import datetime
import pathlib
import json
import yaml
from git import Repo


def read_json(path):
    with open(pathlib.Path(path).absolute().as_posix(), 'r') as file:
        data = json.load(file)

    return data


def write_json(path, data) -> str:
    path = pathlib.Path(path)
    with open(path.absolute().as_posix(), 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return path.as_posix()


def write_yaml(path: str | pathlib.Path, data) -> str:
    path = pathlib.Path(path)
    with open(path.absolute().as_posix(), 'w+') as file:
        yaml.dump(
            data,
            file,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    return path.as_posix()


def datetime_now():
    return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")


