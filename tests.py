import application

errors = []

for number in range(1, 4):
    number = 2
    input_sql = f'tests/test_{number}_input.sql'
    expected_sql = application.main(application.get_sql(f'tests/test_{number}_expected.sql'))

    actual_sql = application.main(application.get_sql(input_sql))
    if expected_sql != actual_sql:
        print(input_sql)
        print(expected_sql)
        print('-------------------------------------------------------------')
        print(actual_sql)