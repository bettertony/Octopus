from base import octopus, clean_db
import os
import tempfile
import time


def test_multiple_insert(octopus, clean_db):
  octopus.create_stream('stream0', x='int')
  octopus.create_stream('stream1', x='int')
  octopus.create_stream('stream2', x='int')

  octopus.create_cv('cv0', 'SELECT count(*) FROM stream1')
  octopus.create_cv('cv1', 'SELECT count(*) FROM stream2')
  octopus.create_ct('ct1', 'SELECT x::int FROM stream0 WHERE mod(x, 2) = 0', "octopus_stream_insert('stream1', 'stream2')")

  octopus.insert('stream0', ('x',), [(n,) for n in range(1000)])

  count = octopus.execute('SELECT count FROM cv0').first()['count']
  assert count == 500
  count = octopus.execute('SELECT count FROM cv1').first()['count']
  assert count == 500


def test_nested_transforms(octopus, clean_db):
  octopus.create_stream('stream0', x='int')
  octopus.create_stream('stream2', x='int')
  octopus.create_stream('stream4', x='int')

  octopus.create_cv('cv0', 'SELECT count(*) FROM stream4')
  octopus.create_cv('cv1', 'SELECT count(*) FROM stream2')
  octopus.create_ct('ct0', 'SELECT x::int FROM stream2 WHERE mod(x, 4) = 0',
                     "octopus_stream_insert('stream4')")
  octopus.create_ct('ct1', 'SELECT x::int FROM stream0 WHERE mod(x, 2) = 0',
                     "octopus_stream_insert('stream2')")

  octopus.insert('stream0', ('x',), [(n,) for n in range(1000)])

  count = octopus.execute('SELECT count FROM cv0').first()['count']
  assert count == 250
  count = octopus.execute('SELECT count FROM cv1').first()['count']
  assert count == 500


def test_deadlock_regress(octopus, clean_db):
  nitems = 2000000
  tmp_file = os.path.join(tempfile.gettempdir(), 'tmp.json')
  query = 'SELECT generate_series(1, %d) AS n' % nitems
  octopus.execute("COPY (%s) TO '%s'" % (query, tmp_file))

  octopus.create_stream('s1', n='int')
  octopus.create_stream('s2', n='int')
  octopus.create_ct('ct', 'SELECT n FROM s1 WHERE n IS NOT NULL',
                     "octopus_stream_insert('s2')")
  octopus.create_cv('cv', 'SELECT count(*) FROM s2')

  for copy in [True, False]:
    for nworkers in [1, 4]:
      for sync in ['receive', 'commit']:
        octopus.stop()
        octopus.run({
          'continuous_query_num_workers': nworkers,
          'stream_insert_level': 'sync_%s' % sync
          })

        octopus.execute("SELECT truncate_continuous_view('cv')")
        octopus.execute('COMMIT')

        if copy:
          octopus.execute("COPY s1 (n) FROM '%s'" % tmp_file)
        else:
          octopus.execute('INSERT INTO s1 (n) %s' % query)

        count = dict(octopus.execute('SELECT count FROM cv').first() or {})
        ntries = 5
        while count.get('count') != nitems and ntries > 0:
          assert sync == 'receive'
          time.sleep(1)
          count = dict(octopus.execute('SELECT count FROM cv').first() or {})
          ntries -= 1
        assert count and count['count'] == nitems

  os.remove(tmp_file)

  octopus.stop()
  octopus.run()
