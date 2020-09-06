import os
import random

import application
from os import walk


class SQL:
    def __init__(self, actual: str, expected: str):
        self.actual: str = actual
        self.expected: str = expected


def get_file_names_with_expected(path):
    all_file_names = []
    for (dir_path, dir_names, file_names) in walk(path):
        all_file_names.extend(file_names)
        break
    expected_file_names = []
    for file_name in all_file_names:
        if "_expected.sql" in file_name:
            expected_file_names.append(file_name)
    return expected_file_names


def preform_tests():
    path = "company_code"
    first_error = None
    for file_name in get_file_names_with_expected(path):
        input_path = f"{path}/{file_name.replace('_expected', '')}"
        print(input_path)
        actual_sql = application.main(application.get_sql(input_path))
        expected_sql = application.get_sql(f"{path}/{file_name}")
        if actual_sql != expected_sql:
            print(file_name)
            first_error = SQL(actual_sql, expected_sql)
            break

    if first_error is not None:
        actual_path = f"company_code/{random.randint(0,10000)}_actual.sql"
        expected_path = f"company_code/{random.randint(0,10000)}_expected.sql"

        with open(actual_path, "w") as file:
            file.write(first_error.actual)
        with open(expected_path, "w") as file:
            file.write(first_error.expected)

        os.system(f"diff {actual_path} {expected_path}")

        os.remove(actual_path)
        os.remove(expected_path)


if __name__ == "__main__":
    preform_tests()
