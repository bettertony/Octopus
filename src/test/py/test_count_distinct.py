from base import octopus, clean_db
import random


def test_hll_count_distinct(octopus, clean_db):
    """
    Verify that streaming COUNT(DISTINCT) works
    """
    octopus.create_stream('stream0', x='int')
    q = 'SELECT COUNT(DISTINCT x::integer) FROM stream0'
    octopus.create_cv('test_count_distinct', q)

    desc = ('x',)
    values = [(random.randint(1, 1024),) for n in range(1000)]

    octopus.insert('stream0', desc, values)

    expected = len(set(values))
    result = octopus.execute('SELECT count FROM test_count_distinct').first()

    # Error rate should be well below %2
    delta = abs(expected - result['count'])

    assert delta / float(expected) <= 0.02
