from base import octopus, clean_db
import os
import subprocess
import time


def _dump(octopus, out_filename, tables=[], data_only=False, schema_only=False):
  out = open(out_filename, 'w')
  cmd = [os.path.join(octopus.bin_dir, 'octopus-dump'), '-p', str(octopus.port), '-d', 'octopus']
  for table in tables:
    cmd += ['-t', table]
  if data_only:
    cmd += ['-a']
  if schema_only:
    cmd += ['-s']
  subprocess.Popen(cmd, stdout=out).communicate()
  out.close()

def _restore(octopus, in_filename):
  cmd = [os.path.join(octopus.bin_dir, 'octopus'), '-p', str(octopus.port), '-d', 'octopus', '-f', in_filename]
  subprocess.Popen(cmd).communicate()
  os.remove(in_filename)


def test_dump(octopus, clean_db):
  """
  Verify that we can dump and restore CVs using INSERT statements
  """
  octopus.create_stream('stream0', x='int')
  q = """
  SELECT x::integer %% 100 AS g, avg(x) + 1 AS avg, count(*), count(distinct x) AS distincts FROM stream0
  GROUP BY g
  """
  octopus.create_cv('test_dump', q)

  rows = [(x,) for x in range(1000)]
  octopus.insert('stream0', ('x',), rows)

  def _verify():
    result = octopus.execute('SELECT count(*) FROM test_dump').first()
    assert result['count'] == 100

    result = octopus.execute('SELECT sum(avg) FROM test_dump').first()
    assert result['sum'] == 50050

    result = octopus.execute('SELECT sum(distincts) FROM test_dump').first()
    assert result['sum'] == 1000

  _verify()
  _dump(octopus, 'test_dump.sql')

  octopus.drop_all()
  _restore(octopus, 'test_dump.sql')
  _verify()

  # Now verify that we can successfully add more data to the restored CV
  rows = [(x,) for x in range(2000)]
  octopus.insert('stream0', ('x',), rows)

  result = octopus.execute('SELECT sum(count) FROM test_dump').first()
  assert result['sum'] == 3000

  result = octopus.execute('SELECT sum(distincts) FROM test_dump').first()
  assert result['sum'] == 2000

def test_sliding_windows(octopus, clean_db):
  """
  Verify that sliding window queries are properly dumped and restored
  """
  octopus.create_stream('stream0', x='int')
  octopus.execute('CREATE CONTINUOUS VIEW sw_v WITH (sw = \'20 seconds\') AS SELECT count(*) FROM stream0')
  octopus.insert('stream0', ('x',), [(x,) for x in range(10)])

  result = octopus.execute('SELECT count FROM sw_v').first()
  assert result['count'] == 10

  _dump(octopus, 'test_sw.sql')

  octopus.drop_all()
  _restore(octopus, 'test_sw.sql')

  result = octopus.execute('SELECT count FROM sw_v').first()
  assert result['count'] == 10

  # We should still drop back to 0 within 20 seconds
  result = octopus.execute('SELECT count FROM sw_v').first()
  while result['count'] > 0:
    time.sleep(1)
    result = octopus.execute('SELECT count FROM sw_v').first()

  result = octopus.execute('SELECT count FROM sw_v').first()
  assert result['count'] == 0

def test_single_continuous_view(octopus, clean_db):
  """
  Verify that specific continuous views can be dropped and restored
  """
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('test_single0', 'SELECT COUNT(*) FROM stream0')
  octopus.create_cv('test_single1', 'SELECT COUNT(*) FROM stream0')
  octopus.insert('stream0', ('x',), [(x,) for x in range(10)])

  result = octopus.execute('SELECT count FROM test_single0').first()
  assert result['count'] == 10

  result = octopus.execute('SELECT count FROM test_single1').first()
  assert result['count'] == 10

  _dump(octopus, 'test_single.sql', tables=['test_single0', 'stream0', 'test_single0_mrel'])

  octopus.drop_all()
  _restore(octopus, 'test_single.sql')

  result = octopus.execute('SELECT count FROM test_single0').first()
  assert result['count'] == 10

  # We didn't dump this one
  result = list(octopus.execute('SELECT * FROM pg_class WHERE relname LIKE \'%%test_single1%%\''))
  assert not result

def test_dump_data_only(octopus, clean_db):
  """
  Verify that it is possible to only dump continuous view data and not schemas
  """
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('test_data', 'SELECT COUNT(*) FROM stream0')
  octopus.insert('stream0', ('x',), [(x,) for x in range(10)])

  result = octopus.execute('SELECT count FROM test_data').first()
  assert result['count'] == 10

  _dump(octopus, 'test_data.sql', data_only=True)

  octopus.drop_all()

  octopus.create_stream('stream0', x='int')
  octopus.create_cv('test_data', 'SELECT COUNT(*) FROM stream0')
  _restore(octopus, 'test_data.sql')

  result = octopus.execute('SELECT count FROM test_data').first()
  assert result['count'] == 10

def test_schema_only(octopus, clean_db):
  """
  Verify that it is possible to only dump continuous view schemas and not data
  """
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('test_schema', 'SELECT COUNT(*) FROM stream0')
  octopus.insert('stream0', ('x',), [(x,) for x in range(10)])

  result = octopus.execute('SELECT count FROM test_schema').first()
  assert result['count'] == 10

  _dump(octopus, 'test_schema.sql', schema_only=True)

  octopus.drop_all()
  _restore(octopus, 'test_schema.sql')

  # No data loaded
  result = list(octopus.execute('SELECT count FROM test_schema'))
  assert not result

def test_static_streams(octopus, clean_db):
  """
  Verify that static stream definitions are dumped and restored
  """
  octopus.create_stream('static', x='int', y='float8')

  _dump(octopus, 'test_static.sql')

  octopus.drop_stream('static')
  _restore(octopus, 'test_static.sql')

  # Force the requirement of a static stream
  octopus.create_cv('static_cv', 'SELECT x, y FROM static')
  octopus.insert('static', ('x', 'y'), [(0, 1)])

  result = octopus.execute('SELECT x, y FROM static_cv').first()
  assert result['x'] == 0
  assert result['y'] == 1

def test_cont_transforms(octopus, clean_db):
  octopus.execute('CREATE STREAM cv_stream (x int, y text)')
  octopus.execute('CREATE STREAM ct_stream (x int, y text)')
  octopus.create_cv('test_cv', 'SELECT count(*) FROM cv_stream')
  octopus.create_ct('test_ct1', 'SELECT x::int, y::text FROM ct_stream WHERE mod(x, 2) = 0',
                     "octopus_stream_insert('cv_stream', 'cv_stream')")
  octopus.create_table('test_t', x='int', y='text')
  octopus.execute('''
  CREATE OR REPLACE FUNCTION test_tg()
  RETURNS trigger AS
  $$
  BEGIN
   INSERT INTO test_t (x, y) VALUES (NEW.x, NEW.y);
   RETURN NEW;
  END;
  $$
  LANGUAGE plpgsql;
  ''')
  octopus.create_ct('test_ct2', 'SELECT x::int, y::text FROM ct_stream',
                     'test_tg()')

  octopus.insert('ct_stream', ('x', 'y'), [(1, 'hello'), (2, 'world')])
  time.sleep(1)

  _dump(octopus, 'test_cont_transform.sql')

  octopus.drop_all()
  octopus.drop_table('test_t')
  octopus.execute('DROP FUNCTION test_tg()')

  _restore(octopus, 'test_cont_transform.sql')

  octopus.insert('ct_stream', ('x', 'y'), [(1, 'hello'), (2, 'world')])
  time.sleep(1)

  assert octopus.execute('SELECT count FROM test_cv').first()['count'] == 4
  ntups = 0
  for row in octopus.execute('SELECT x, count(*) FROM test_t GROUP BY x'):
    assert row['count'] == 2
    assert row['x'] in (1, 2)
    ntups += 1
  assert ntups == 2
