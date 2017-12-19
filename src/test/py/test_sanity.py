from base import async_insert, octopus, clean_db

import getpass
import os
import psycopg2
import tempfile
import threading
import time


def test_create_drop_continuous_view(octopus, clean_db):
  """
  Basic sanity check
  """
  octopus.create_stream('stream0', id='int')
  octopus.create_cv('cv0', 'SELECT id::integer FROM stream0')
  octopus.create_cv('cv1', 'SELECT id::integer FROM stream0')
  octopus.create_cv('cv2', 'SELECT id::integer FROM stream0')

  result = octopus.execute('SELECT * FROM octopus_views()')
  names = [r['name'] for r in result]

  assert sorted(names) == ['cv0', 'cv1', 'cv2']

  octopus.drop_cv('cv0')
  octopus.drop_cv('cv1')
  octopus.drop_cv('cv2')

  result = octopus.execute('SELECT * FROM octopus_views()')
  names = [r['name'] for r in result]

  assert len(names) == 0


def test_simple_insert(octopus, clean_db):
  """
  Verify that we can insert some rows and count some stuff
  """
  octopus.create_stream('stream0', key='int')
  octopus.create_cv('cv',
                     'SELECT key::integer, COUNT(*) FROM stream0 GROUP BY key')

  rows = [(n % 10,) for n in range(1000)]

  octopus.insert('stream0', ('key',), rows)

  result = list(octopus.execute('SELECT * FROM cv ORDER BY key'))

  assert len(result) == 10
  for i, row in enumerate(result):
    assert row['key'] == i
    assert row['count'] == 100


def test_multiple(octopus, clean_db):
  """
  Verify that multiple continuous views work together properly
  """
  octopus.create_stream('stream0', n='numeric', s='text', unused='int')
  octopus.create_cv('cv0', 'SELECT n::numeric FROM stream0 WHERE n > 10.00001')
  octopus.create_cv('cv1',
                     'SELECT s::text FROM stream0 WHERE s LIKE \'%%this%%\'')

  rows = [(float(n + 10), 'this', 100) for n in range(1000)]
  for n in range(10):
    rows.append((float(n), 'not a match', -n))

  octopus.insert('stream0', ('n', 's', 'unused'), rows)

  result = list(octopus.execute('SELECT * FROM cv0'))
  assert len(result) == 999

  result = list(octopus.execute('SELECT * FROM cv1'))
  assert len(result) == 1000


def test_combine(octopus, clean_db):
  """
  Verify that partial tuples are combined with on-disk tuples
  """
  octopus.create_stream('stream0', key='text', unused='int')
  octopus.create_cv('combine',
                     'SELECT key::text, COUNT(*) FROM stream0 GROUP BY key')

  rows = []
  for n in range(100):
    for m in range(100):
      key = '%d%d' % (n % 10, m)
      rows.append((key, 0))

  octopus.insert('stream0', ('key', 'unused'), rows)

  total = 0
  result = octopus.execute('SELECT * FROM combine')
  for row in result:
    total += row['count']

  assert total == 10000


def test_multiple_stmts(octopus, clean_db):
  octopus.create_stream('stream0', unused='int')
  conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s'
                          % (getpass.getuser(), octopus.port))
  db = conn.cursor()
  db.execute('CREATE CONTINUOUS VIEW test_multiple AS '
             'SELECT COUNT(*) FROM stream0; SELECT 1;')
  conn.commit()
  conn.close()

  octopus.insert('stream0', ('unused',), [(1,)] * 100)

  result = list(octopus.execute('SELECT * FROM test_multiple'))
  assert len(result) == 1
  assert result[0]['count'] == 100


def test_uniqueness(octopus, clean_db):
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('uniqueness',
                     'SELECT x::int, count(*) FROM stream0 GROUP BY x')

  for i in range(10):
    rows = [((10000 * i) + j,) for j in xrange(10000)]
    octopus.insert('stream0', ('x',), rows)

  count = octopus.execute('SELECT count(*) FROM uniqueness').first()['count']
  distinct_count = octopus.execute(
    'SELECT count(DISTINCT x) FROM uniqueness').first()['count']

  assert count == distinct_count

@async_insert
def test_concurrent_inserts(octopus, clean_db):
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('concurrent_inserts0',
                     'SELECT x::int, count(*) FROM stream0 GROUP BY x')
  octopus.create_cv('concurrent_inserts1', 'SELECT count(*) FROM stream0')

  num_threads = 4
  stop = False
  inserted = [0] * num_threads

  def insert(i):
    conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s'
                            % (getpass.getuser(), octopus.port))
    cur = conn.cursor()
    while not stop:
      cur.execute('INSERT INTO stream0 (x) '
                  'SELECT x % 100 FROM generate_series(1, 2000) AS x')
      conn.commit()
      inserted[i] += 2000
    conn.close()

  threads = [threading.Thread(target=insert, args=(i,))
             for i in range(num_threads)]
  map(lambda t: t.start(), threads)

  time.sleep(60)

  stop = True
  map(lambda t: t.join(), threads)

  time.sleep(5)

  total = (octopus.execute('SELECT sum(count) FROM concurrent_inserts0')
           .first()['sum'])
  assert total == sum(inserted)

  total = (octopus.execute('SELECT count FROM concurrent_inserts1')
           .first()['count'])
  assert total == sum(inserted)

@async_insert
def test_concurrent_copy(octopus, clean_db):
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('concurrent_copy0',
                     'SELECT x::int, count(*) FROM stream0 GROUP BY x')
  octopus.create_cv('concurrent_copy1', 'SELECT count(*) FROM stream0')

  tmp_file = os.path.join(tempfile.gettempdir(), 'tmp.copy')
  query = 'SELECT generate_series(1, 2000) AS x'
  octopus.execute("COPY (%s) TO '%s'" % (query, tmp_file))

  num_threads = 4
  stop = False
  inserted = [0] * num_threads

  def insert(i):
    conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s'
                            % (getpass.getuser(), octopus.port))
    cur = conn.cursor()
    while not stop:
      cur.execute("COPY stream0 (x) FROM '%s'" % tmp_file)
      conn.commit()
      inserted[i] += 2000
    conn.close()

  threads = [threading.Thread(target=insert, args=(i,))
             for i in range(num_threads)]
  map(lambda t: t.start(), threads)

  time.sleep(60)

  stop = True
  map(lambda t: t.join(), threads)

  time.sleep(5)

  total = (octopus.execute('SELECT sum(count) FROM concurrent_copy0')
           .first()['sum'])
  assert total == sum(inserted)

  total = (octopus.execute('SELECT count FROM concurrent_copy1')
           .first()['count'])
  assert total == sum(inserted)
