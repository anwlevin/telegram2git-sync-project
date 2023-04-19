import datetime
import pathlib
import json

from git import Repo


def read_json(path):
    with open(pathlib.Path(path).absolute().as_posix(), 'r') as f:
        data = json.load(f)

    return data


def write_json(path, data) -> str:
    path = pathlib.Path(path)
    with open(path.absolute().as_posix(), 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return path.as_posix()


def datetime_now():
    return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")


def repo_add_file_commit_and_push(repo_path, file_path):
    repo = Repo(pathlib.Path(repo_path).absolute().as_posix())
    file = pathlib.Path(file_path)
    repo.index.add([file.as_posix()])

    comment = f'Add {file.name} at {datetime_now()}'
    repo.index.commit(comment)
    repo.remote('origin').push()

