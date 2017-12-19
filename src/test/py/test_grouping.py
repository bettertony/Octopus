from base import octopus, clean_db
import random


def test_null_groups(octopus, clean_db):
    """
    Verify that null group columns are considered equal
    """
    octopus.create_stream('s', x='int', y='int', z='int')
    q = """
    SELECT x::integer, y::integer, z::integer, COUNT(*) FROM s
    GROUP BY x, y, z;
    """
    desc = ('x', 'y', 'z')
    octopus.create_cv('test_null_groups', q)
    octopus.create_table('test_null_groups_t', x='integer', y='integer', z='integer')

    rows = []
    for n in range(10000):
        vals = list(random.randint(0, 10) for n in range(3))
        vals = map(lambda n: random.random() > 0.1 and n or None, vals)
        rows.append(tuple(vals))

    octopus.insert('s', desc, rows)
    octopus.insert('test_null_groups_t', desc, rows)

    table_q = """
    SELECT x, y, z, COUNT(*) FROM test_null_groups_t
    GROUP BY x, y, z ORDER BY x, y, z;
    """
    expected = list(octopus.execute(table_q))
    result = list(octopus.execute('SELECT x, y, z, count FROM test_null_groups ORDER BY x, y, z'))

    for r, e in zip(result, expected):
        assert r == e
