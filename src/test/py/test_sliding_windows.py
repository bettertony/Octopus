from base import octopus, clean_db
import time


def assert_result_changes(func, args):
    """
    Verifies that the result of the given function changes with time
    """
    octopus.create_stream('stream0', x='int', y='text', z='int')
    name = 'assert_%s_decreases' % func
    octopus.create_cv(name,
                       "SELECT %s(%s) FROM stream0 WHERE arrival_timestamp > clock_timestamp() - interval '2 seconds'" % (func, args))

    rows = [(n, str(n), n + 1) for n in range(1000)]
    octopus.insert('stream0', ('x', 'y', 'z'), rows)

    current = 1

    results = []
    while current:
        row = octopus.execute('SELECT * FROM %s' % name).first()
        current = row[func]
        if current is None:
            break
        results.append(current)

    # Verify that we actually read something
    assert results

    octopus.drop_cv(name)

def test_count(octopus, clean_db):
    """
    count
    """
    assert_result_changes('count', '*')

def test_avg(octopus, clean_db):
    """
    avg
    """
    assert_result_changes('avg', 'x::integer')

def test_sum(octopus, clean_db):
    """
    sum
    """
    assert_result_changes('sum', 'x::integer')

def test_array_agg(octopus, clean_db):
    """
    array_agg
    """
    assert_result_changes('array_agg', 'x::integer')

def test_json_agg(octopus, clean_db):
    """
    json_agg
    """
    assert_result_changes('json_agg', 'x::integer')

def test_regr_sxx(octopus, clean_db):
    """
    regr_sxx
    """
    assert_result_changes('regr_sxx', 'x::float8, x::float8')

def test_regr_syy(octopus, clean_db):
    """
    regr_syy
    """
    assert_result_changes('regr_syy', 'x::float8, x::float8')

def test_regr_sxy(octopus, clean_db):
    """
    regr_sxy
    """
    assert_result_changes('regr_sxy', 'x::float8, x::float8')

def test_regr_avgx(octopus, clean_db):
    """
    regr_avgx
    """
    assert_result_changes('regr_avgx', 'x::float8, x::float8')

def test_regr_avgy(octopus, clean_db):
    """
    regr_avgy
    """
    assert_result_changes('regr_avgy', 'x::float8, x::float8')

def test_regr_r2(octopus, clean_db):
    """
    regr_r2
    """
    assert_result_changes('regr_r2', 'x::float8, x::float8')

def test_regr_slope(octopus, clean_db):
    """
    regr_slope
    """
    assert_result_changes('regr_slope', 'x::float8, x::float8')

def test_regr_intercept(octopus, clean_db):
    """
    regr_intercept
    """
    assert_result_changes('regr_intercept', 'x::float8, z::float8')

def test_covar_pop(octopus, clean_db):
    """
    covar_pop
    """
    assert_result_changes('covar_pop', 'x::float8, x::float8')

def test_covar_samp(octopus, clean_db):
    """
    covar_samp
    """
    assert_result_changes('covar_samp', 'x::float8, x::float8')

def test_corr(octopus, clean_db):
    """
    corr
    """
    assert_result_changes('corr', 'x::float8, x::float8')

def test_var_pop(octopus, clean_db):
    """
    var_pop
    """
    assert_result_changes('var_pop', 'x::float8')

def test_var_samp(octopus, clean_db):
    """
    var_samp
    """
    assert_result_changes('var_samp', 'x::float8')

def test_stddev_samp(octopus, clean_db):
    """
    stddev_samp
    """
    assert_result_changes('stddev_samp', 'x::float8')

def test_stddev_pop(octopus, clean_db):
    """
    stddev_pop
    """
    assert_result_changes('stddev_pop', 'x::float8')
