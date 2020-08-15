WITH hello as (SELECT * FROM schema.TABLE) alias_1 SELECT one, two, three, min(four) AS five, six
FROM alias_1
join SCHEMA_2.TABLE_2 alias_2 on alias.one = alias_2.field_one and alias_2.field_three = 3
WHERE alias_1.one = alias_2.field_two and alias_2.field_two = 'three';