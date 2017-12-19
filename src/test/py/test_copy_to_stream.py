from base import octopus, clean_db
import os
import random


def _generate_csv(path, rows, desc=None, delimiter=','):
    csv = open(path, 'wa')
    if desc:
        rows = [desc] + rows
    for row in rows:
        line = delimiter.join(str(v) for v in row) + '\n'
        csv.write(line)
    csv.close()

def test_copy_to_stream(octopus, clean_db):
    """
    Verify that copying data from a file into a stream works
    """
    octopus.create_stream('stream0', x='int', y='float8', z='numeric')
    q = 'SELECT sum(x::integer) AS s0, sum(y::float8) AS s1, avg(z::numeric) FROM stream0'
    octopus.create_cv('test_copy_to_stream', q)
    octopus.create_table('test_copy_to_stream_t', x='integer', y='float8', z='numeric')

    path = os.path.abspath(os.path.join(octopus.tmp_dir, 'test_copy.csv'))

    rows = []
    for n in range(10000):
        row = random.randint(1, 1024), random.randint(1, 1024), random.random()
        rows.append(row)

    _generate_csv(path, rows, desc=('x', 'y', 'z'))

    octopus.execute('COPY test_copy_to_stream_t (x, y, z) FROM \'%s\' HEADER CSV' % path)

    octopus.execute('COPY stream0 (x, y, z) FROM \'%s\' HEADER CSV' % path)

    expected = octopus.execute('SELECT sum(x::integer) AS s0, sum(y::float8) AS s1, avg(z::numeric) FROM test_copy_to_stream_t').first()
    result = list(octopus.execute('SELECT * FROM test_copy_to_stream'))

    assert len(result) == 1

    result = result[0]

    assert result[0] == expected[0]
    assert result[1] == expected[1]
    assert result[2] == expected[2]


def test_colums_subset(octopus, clean_db):
    """
    Verify that copying data from a file into a stream works when the file's input
    columns are a subset of the stream0's columns
    """
    octopus.create_stream('stream0', x='int', y='float8', z='numeric', m='int')
    q = 'SELECT sum(x::integer) AS s0, sum(y::float8) AS s1, avg(z::numeric), max(m::integer) FROM stream0'
    octopus.create_cv('test_copy_subset', q)
    octopus.create_table('test_copy_subset_t', x='integer', y='float8', z='numeric')

    path = os.path.abspath(os.path.join(octopus.tmp_dir, 'test_copy.csv'))

    rows = []
    for n in range(10000):
        row = random.randint(1, 1024), random.randint(1, 1024), random.random()
        rows.append(row)

    _generate_csv(path, rows, desc=('x', 'y', 'z'))

    octopus.execute('COPY test_copy_subset_t (x, y, z) FROM \'%s\' HEADER CSV' % path)

    octopus.execute('COPY stream0 (x, y, z) FROM \'%s\' HEADER CSV' % path)

    expected = octopus.execute('SELECT sum(x::integer) AS s0, sum(y::float8) AS s1, avg(z::numeric) FROM test_copy_subset_t').first()
    result = list(octopus.execute('SELECT s0, s1, avg FROM test_copy_subset'))

    assert len(result) == 1

    result = result[0]

    assert result[0] == expected[0]
    assert result[1] == expected[1]
    assert result[2] == expected[2]

def test_regression(octopus, clean_db):
  path = os.path.abspath(os.path.join(octopus.tmp_dir, 'test_copy.csv'))
  _generate_csv(path, [['2015-06-01 00:00:00', 'De', 'Adam_Babareka', '1', '37433']], desc=('day', 'project', 'title', 'count', 'size'))

  octopus.create_stream('copy_regression_stream', count='int', day='timestamp', project='text', title='text', size='int')
  octopus.create_cv('test_copy_regression', 'SELECT sum(count) FROM copy_regression_stream')

  octopus.execute("COPY copy_regression_stream (day, project, title, count, size) FROM '%s' CSV HEADER" % path)
