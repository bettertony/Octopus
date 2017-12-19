from base import octopus, clean_db

import random

def get_geometric_dist(items):
  values = map(lambda i: [i] * pow(2, items.index(i)), items)
  values = sum(values, [])
  random.shuffle(values)
  return values


def test_fss_agg(octopus, clean_db):
  octopus.create_stream('test_fss_stream', x='int', k='text')
  q = """
  SELECT k::text, fss_agg(x::int, 5) FROM test_fss_stream
  GROUP BY k
  """
  desc = ('k', 'x')
  octopus.create_cv('test_fss_agg', q)

  items = range(14)
  random.shuffle(items)
  a_items = items
  b_items = list(reversed(items))

  values = map(lambda i: ('a', i), get_geometric_dist(a_items))
  values.extend(map(lambda i: ('b', i), get_geometric_dist(b_items)))
  random.shuffle(values)

  octopus.insert('test_fss_stream', desc, values)
  result = list(octopus.execute('SELECT k, fss_topk_values(fss_agg) FROM test_fss_agg ORDER BY k'))
  topk = map(int, result[0][1].rstrip('}').lstrip('{').split(','))
  assert sorted(topk) == sorted(a_items[-5:])
  topk = map(int, result[1][1].rstrip('}').lstrip('{').split(','))
  assert sorted(topk) == sorted(b_items[-5:])
