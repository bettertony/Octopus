import random

from base import octopus, clean_db

# XXX(usmanm): update this, if it ever changes!
MAX_CQS = 1024

def test_create_views(octopus, clean_db):
  cvs = []
  octopus.create_stream('stream0', x='int')
  q = 'SELECT count(*) FROM stream0'

  for i in xrange(1, MAX_CQS):
    cvs.append('cv_%d' % i)
    octopus.create_cv(cvs[-1], q)

  try:
    octopus.create_cv('cv_fail', q)
    assert False
  except Exception, e:
    assert 'maximum number of continuous queries exceeded' in e.message

  ids = [r['id'] for r in
         octopus.execute('SELECT id FROM octopus_views()')]

  assert len(set(ids)) == len(ids)
  assert set(ids) == set(xrange(1, MAX_CQS))

  num_remove = random.randint(128, 512)

  for _ in xrange(num_remove):
    octopus.drop_cv(cvs.pop())

  for _ in xrange(num_remove):
    cvs.append('cv_%d' % (len(cvs) + 1))
    octopus.create_cv(cvs[-1], q)
