from base import octopus, clean_db
import time


def test_output_tree(octopus, clean_db):
  """
  Create a relatively complex tree of continuous views
  and transforms chained together by their output streams,
  and verify that all output correctly propagates to the leaves.
  """
  octopus.create_stream('root', x='int')
  octopus.create_cv('level0_0', 'SELECT x::integer, count(*) FROM root GROUP BY x')

  octopus.create_cv('level1_0', 'SELECT (new).x, (new).count FROM level0_0_osrel')
  octopus.create_cv('level1_1', 'SELECT (new).x, (new).count FROM level0_0_osrel')

  octopus.create_cv('level2_0', 'SELECT (new).x, (new).count FROM level1_0_osrel')
  octopus.create_cv('level2_1', 'SELECT (new).x, (new).count FROM level1_0_osrel')
  octopus.create_cv('level2_2', 'SELECT (new).x, (new).count FROM level1_1_osrel')
  octopus.create_cv('level2_3', 'SELECT (new).x, (new).count FROM level1_1_osrel')

  octopus.create_cv('level3_0', 'SELECT (new).x, (new).count FROM level2_0_osrel')
  octopus.create_cv('level3_1', 'SELECT (new).x, (new).count FROM level2_0_osrel')
  octopus.create_cv('level3_2', 'SELECT (new).x, (new).count FROM level2_1_osrel')
  octopus.create_cv('level3_3', 'SELECT (new).x, (new).count FROM level2_1_osrel')
  octopus.create_cv('level3_4', 'SELECT (new).x, (new).count FROM level2_2_osrel')
  octopus.create_cv('level3_5', 'SELECT (new).x, (new).count FROM level2_2_osrel')
  octopus.create_cv('level3_6', 'SELECT (new).x, (new).count FROM level2_3_osrel')
  octopus.create_cv('level3_7', 'SELECT (new).x, (new).count FROM level2_3_osrel')

  octopus.insert('root', ('x',), [(x % 100,) for x in range(10000)])

  names = [r[0] for r in octopus.execute('SELECT name FROM octopus_views() ORDER BY name DESC')]
  assert len(names) == 15

  # Verify all values propagated to each node in the tree
  for name in names:
    rows = octopus.execute('SELECT x, max(count) FROM %s GROUP BY x' % name)
    for row in rows:
      x, count = row
      assert count == 100

  octopus.insert('root', ('x',), [(x % 100,) for x in range(10000)])

  # Verify all values propagated to each node in the tree again
  for name in names:
    rows = octopus.execute('SELECT x, max(count) FROM %s GROUP BY x' % name)
    for row in rows:
      x, count = row
      assert count == 200

  # Drop these in reverse dependency order to prevent deadlocks
  for name in names:
    octopus.drop_cv(name)


def test_concurrent_sw_ticking(octopus, clean_db):
  """
  Verify that several concurrent sliding-window queries each
  having different windows tick correctly at different intervals.
  """
  octopus.create_stream('stream0', x='int')
  output_names = []
  for n in range(10):
    name = 'sw%d' % n
    octopus.create_cv(name, 'SELECT x::integer, count(*) FROM stream0 GROUP BY x', sw='%d seconds' % (n + 10))
    output_name = name + '_output'

    q = """
    SELECT arrival_timestamp,
    CASE WHEN (old).x IS NULL THEN (new).x ELSE (old).x END AS x, old, new FROM %s_osrel
    """ % name
    octopus.create_cv(output_name, q)
    output_names.append(output_name)

  names = [r[0] for r in octopus.execute('SELECT name FROM octopus_views() ORDER BY name DESC')]
  assert len(names) == 2 * 10

  octopus.insert('stream0', ('x',), [(x % 100,) for x in range(10000)])
  time.sleep(25)

  for name in output_names:
    rows = list(octopus.execute('SELECT COUNT(DISTINCT x) FROM %s' % name))
    assert rows[0][0] == 100

    for x in range(100):
      # In window
      assert octopus.execute('SELECT * FROM %s WHERE old IS NULL AND new IS NOT NULL AND x = %d' % (name, x))
      # Out of window
      assert octopus.execute('SELECT * FROM %s WHERE old IS NOT NULL AND new IS NULL AND x = %d' % (name, x))

  # Drop these in reverse dependency order to prevent deadlocks
  for name in names:
    octopus.drop_cv(name)


def test_transforms(octopus, clean_db):
  """
  Verify that continuous transforms work properly on output streams
  """
  octopus.create_stream('stream0', x='int')
  octopus.create_cv('sw', 'SELECT x::integer, COUNT(*) FROM stream0 GROUP BY x',
                     sw='5 seconds')

  # Write a row to a stream each time a row goes out of window
  q = 'SELECT (old).x FROM sw_osrel WHERE old IS NOT NULL AND new IS NULL'
  octopus.create_stream('oow_stream', x='integer')
  octopus.create_ct('ct', q, "octopus_stream_insert('oow_stream')")
  octopus.create_cv('ct_recv', 'SELECT x FROM oow_stream')

  octopus.insert('stream0', ('x',), [(x % 100,) for x in range(10000)])
  time.sleep(7)

  rows = list(octopus.execute('SELECT * FROM ct_recv'))
  assert len(rows) == 100
