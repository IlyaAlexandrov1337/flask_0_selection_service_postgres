import json
from data import goals, teachers


def open_json(name):
    with open(f"{name}", "r", encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    with open("database_json/goals.json", "w", encoding='utf-8') as f:
        json.dump(goals, f)

    with open("database_json/teachers.json", "w", encoding='utf-8') as f:
        json.dump(teachers, f)

