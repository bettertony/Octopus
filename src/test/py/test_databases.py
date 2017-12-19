from base import octopus, clean_db
import getpass
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_multiple_databases(octopus, clean_db):
  conn = psycopg2.connect('dbname=octopus user=%s host=localhost port=%s' % (getpass.getuser(), octopus.port))
  conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

  cur = conn.cursor()
  cur.execute('CREATE DATABASE tmp_octopus')
  cur.close()

  q = 'SELECT x::int FROM dbstream'
  octopus.create_stream('dbstream', x='int')
  octopus.create_cv('test_multiple_databases', q)

  # Insert data in first database.
  octopus.insert('dbstream', ['x'], map(lambda x: (x,), range(0, 10, 2)))
  result = octopus.execute('SELECT * FROM test_multiple_databases')
  assert sorted(row['x'] for row in result) == range(0, 10, 2)

  # Create same CV in the other database, make sure its created and write different data to it.
  tmp_conn = psycopg2.connect('dbname=tmp_octopus user=%s host=localhost port=%s' % (getpass.getuser(), octopus.port))
  cur = tmp_conn.cursor()
  cur.execute('CREATE STREAM dbstream (x int)')
  cur.execute('CREATE CONTINUOUS VIEW test_multiple_databases AS %s' % q)
  tmp_conn.commit()
  cur.execute('INSERT INTO dbstream (x) VALUES %s' % ', '.join(map(lambda x: '(%d)' % x, range(1, 11, 2))))
  cur.execute('SELECT * FROM test_multiple_databases')
  tmp_conn.commit()
  assert sorted(row[0] for row in cur) == range(1, 11, 2)

  # Ensure that the data written to the other database isn't seen by the first database.
  result = octopus.execute('SELECT * FROM test_multiple_databases')
  assert sorted(row['x'] for row in result) == range(0, 10, 2)

  # Insert new data to both databases.
  octopus.insert('dbstream', ['x'], map(lambda x: (x,), range(10, 20, 2)))
  cur.execute('INSERT INTO dbstream (x) VALUES %s' % ', '.join(map(lambda x: '(%d)' % x, range(11, 21, 2))))

  # Ensure both databases still saw the data written out to them.
  result = octopus.execute('SELECT * FROM test_multiple_databases')
  assert sorted(row['x'] for row in result) == range(0, 20, 2)
  cur.execute('SELECT * FROM test_multiple_databases')
  tmp_conn.commit()
  assert sorted(row[0] for row in cur) == range(1, 21, 2)

  cur.close()
  tmp_conn.close()
  cur = conn.cursor()
  cur.execute('DROP DATABASE tmp_octopus')
  cur.close()
  conn.close()
