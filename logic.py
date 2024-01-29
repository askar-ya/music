import json


def read_from_file(filename):
    """Функция возвращает данные из файла"""
    with open(filename, 'r', encoding='utf8') as f:
        return json.load(f)


def write_to_file(filename, data):
    with open(filename, 'w', encoding='utf8') as f:
        return json.dump(data, f, ensure_ascii=False)
