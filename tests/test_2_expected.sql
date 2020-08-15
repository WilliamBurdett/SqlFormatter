WITH hello AS (
    SELECT * FROM schema.table
) alias_1
SELECT
    one,
    two,
    three,
    MIN(four) AS five,
    six
FROM
    alias_1
    JOIN schema_2.table_2 alias_2
        ON alias.one = alias_2.field_one
            AND alias_2.field_three = 3
    WHERE
        alias_1.one = alias_2.field_two
            AND alias_2.field_two = 'three'