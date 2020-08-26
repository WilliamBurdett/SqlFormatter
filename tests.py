import os
import random

import application
from os import walk


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
    first_error = {}
    for file_name in get_file_names_with_expected(path):
        input_path = f"{path}/{file_name.replace('_expected', '')}"
        actual_sql = application.main(application.get_sql(input_path))
        expected_sql = application.get_sql(f"{path}/{file_name}")
        if actual_sql != expected_sql:
            print(file_name)
            if len(first_error) == 0:
                first_error[actual_sql] = expected_sql

    actual_path = f"company_code/{random.randint(0,10000)}_actual.sql"
    expected_path = f"company_code/{random.randint(0,10000)}_expected.sql"

    with open(actual_path, "w") as file:
        file.write([key for key in first_error.keys()][0])
    with open(expected_path, "w") as file:
        file.write([values for values in first_error.values()][0])

    os.system(f"diff {actual_path} {expected_path}")

    os.remove(actual_path)
    os.remove(expected_path)


if __name__ == "__main__":
    preform_tests()
