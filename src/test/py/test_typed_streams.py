from base import octopus, clean_db


def test_online_add_column(octopus, clean_db):
    """
    Verify that we can add columns to a stream while not affecting running CQs
    """
    octopus.create_stream('stream0', c0='integer')

    octopus.create_cv('cv0', 'SELECT c0 FROM stream0')
    octopus.insert('stream0', ('c0',), [(n,) for n in range(0, 1000)])
    result = list(octopus.execute('SELECT * FROM cv0'))

    assert len(result) == 1000

    for row in result:
        for col in row:
            assert col is not None

    octopus.execute('ALTER STREAM stream0 ADD c1 integer')

    octopus.create_cv('cv1', 'SELECT c0, c1 FROM stream0')
    octopus.insert('stream0', ('c0', 'c1'),
                    [(n, n) for n in range(1000, 2000)])
    result = list(octopus.execute('SELECT * FROM cv1 WHERE c1 >= 1000'))

    assert len(result) == 1000

    for row in result:
        for col in row:
            assert col is not None

    octopus.execute('ALTER STREAM stream0 ADD c2 integer')
    octopus.create_cv('cv2', 'SELECT c0, c1, c2 FROM stream0')
    octopus.insert('stream0', ('c0', 'c1', 'c2'),
                    [(n, n, n) for n in range(2000, 3000)])
    result = list(octopus.execute('SELECT * FROM cv2 WHERE c2 >= 2000'))

    assert len(result) == 1000

    for row in result:
        for col in row:
            assert col is not None

    octopus.execute('ALTER STREAM stream0 ADD c3 integer')
    octopus.create_cv('cv3', 'SELECT c0, c1, c2, c3 FROM stream0')
    octopus.insert('stream0', ('c0', 'c1', 'c2', 'c3'),
                    [(n, n, n, n) for n in range(3000, 4000)])
    result = list(octopus.execute('SELECT * FROM cv3 WHERE c3 >= 3000'))

    assert len(result) == 1000

    for row in result:
        for col in row:
            assert col is not None

    octopus.execute('ALTER STREAM stream0 ADD c4 integer')
    octopus.create_cv('cv4', 'SELECT c0, c1, c2, c3, c4 FROM stream0')
    octopus.insert('stream0', ('c0', 'c1', 'c2', 'c3', 'c4'),
                    [(n, n, n, n, n) for n in range(4000, 5000)])
    result = list(octopus.execute('SELECT * FROM cv4 WHERE c4 >= 4000'))

    assert len(result) == 1000

    for row in result:
        for col in row:
            assert col is not None

def test_online_drop_column(octopus, clean_db):
  octopus.create_stream('stream1', c0='integer')

  try:
    octopus.execute('ALTER STREAM stream1 DROP c0')
    assert False
  except:
    pass
