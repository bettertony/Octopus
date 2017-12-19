from base import async_insert, octopus, clean_db
import getpass
import psycopg2
import threading
import time


def test_combine_table(octopus, clean_db):
  octopus.create_stream('s', x='int')
  octopus.create_cv('combine_table',
                     'SELECT x::int, COUNT(*) FROM s GROUP BY x')

  values = [(i,) for i in xrange(1000)]
  octopus.insert('s', ('x',), values)

  octopus.execute('SELECT * INTO tmprel FROM combine_table_mrel')

  stop = False
  ninserts = [0]

  def insert():
    while not stop:
      octopus.insert('s', ('x',), values)
      ninserts[0] += 1
      time.sleep(0.01)

  t = threading.Thread(target=insert)
  t.start()

  time.sleep(2)

  conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s' %
                          (getpass.getuser(), octopus.port))
  cur = conn.cursor()
  cur.execute("SELECT octopus_combine_table('combine_table', 'tmprel')")
  conn.commit()
  conn.close()

  stop = True
  t.join()

  assert ninserts[0] > 0

  rows = list(octopus.execute('SELECT count FROM combine_table'))
  assert len(rows) == 1000
  for row in rows:
    assert row[0] == ninserts[0] + 2

  octopus.execute('DROP TABLE tmprel')


def test_combine_table_no_groups(octopus, clean_db):
  octopus.create_stream('s', x='int')
  octopus.create_cv('no_groups', 'SELECT COUNT(*) FROM s')
  values = [(i,) for i in xrange(1000)]
  octopus.insert('s', ('x',), values)

  octopus.execute('SELECT * INTO tmprel FROM no_groups_mrel')
  octopus.execute("SELECT octopus_combine_table('no_groups', 'tmprel')")

  rows = list(octopus.execute('SELECT count FROM no_groups'))
  assert len(rows) == 1
  assert len(rows[0]) == 1
  assert rows[0][0] == 2000


def test_octopus_flush(octopus, clean_db):
  octopus.execute('SET stream_insert_level=async')
  octopus.create_stream('s', x='int')
  octopus.create_cv('flush', 'SELECT x, pg_sleep(0.01) FROM s')

  values = [(i,) for i in xrange(1000)]
  start = time.time()

  # This will take 0.01 * 1000 = 10s to process but return immediately since
  # inserts are async and values will fit in one batch.
  octopus.insert('s', ('x',), values)
  insert_end = time.time()

  octopus.execute('SELECT octopus_flush()')
  flush_end = time.time()

  assert insert_end - start < 0.1
  assert flush_end - start > 10

  row = list(octopus.execute('SELECT count(*) FROM flush'))[0]
  assert row[0] == 1000

  octopus.execute('SET stream_insert_level=sync_commit')
