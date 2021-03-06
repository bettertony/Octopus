from base import octopus, clean_db
import getpass
import psycopg2
import threading
import time


def test_userset_sync(octopus, clean_db):
  octopus.create_stream('s', x='int')
  octopus.create_cv('sync',
                     'SELECT count(*) FROM s WHERE x = 0')
  octopus.create_cv('async',
                     'SELECT count(*) FROM s WHERE x = 1')
  octopus.create_cv('delay',
                     'SELECT x::int, pg_sleep(0.1) FROM s')

  NUM_INSERTS = 100

  def insert(sync):
    conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s'
                            % (getpass.getuser(), octopus.port))
    cur = conn.cursor()
    cur.execute('SET stream_insert_level=sync_%s' %
                ('commit' if sync else 'receive'))
    for i in xrange(NUM_INSERTS):
      cur.execute('INSERT INTO s (x) VALUES (%d)' % (0 if sync else 1))
      conn.commit()
    conn.close()

  sync = threading.Thread(target=insert, args=(True,))
  async = threading.Thread(target=insert, args=(False,))

  start = time.time()

  sync.start()
  async.start()

  async.join()
  async_time = time.time() - start
  assert async_time < NUM_INSERTS * 0.1

  num_sync = octopus.execute('SELECT count FROM sync').first()['count']
  num_async = octopus.execute('SELECT count FROM async').first()['count']
  total = octopus.execute('SELECT count(*) FROM delay').first()['count']
  assert num_async < NUM_INSERTS
  assert num_sync < NUM_INSERTS
  assert total < NUM_INSERTS * 2

  sync.join()
  assert time.time() - start > (NUM_INSERTS * 0.08 + async_time)

  octopus.execute('COMMIT')
  num_sync = octopus.execute('SELECT count FROM sync').first()['count']
  num_async = octopus.execute('SELECT count FROM async').first()['count']
  total = octopus.execute('SELECT count(*) FROM delay').first()['count']
  assert num_sync == NUM_INSERTS
  assert num_async == NUM_INSERTS
  assert total == NUM_INSERTS * 2
