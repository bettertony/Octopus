CREATE DATABASE octopus_stats_db;
\c octopus_stats_db

CREATE STREAM test_octopus_stats_stream (x int);
CREATE CONTINUOUS VIEW test_octopus_stats0 AS SELECT COUNT(*) FROM test_octopus_stats_stream;

SELECT pg_sleep(2);
SELECT output_rows, errors, cv_create, cv_drop FROM octopus_stats WHERE type = 'combiner';
SELECT input_rows, input_bytes, errors FROM octopus_stats WHERE type = 'worker';

DROP CONTINUOUS VIEW test_octopus_stats0;

SELECT pg_sleep(2);
SELECT output_rows, errors, cv_create, cv_drop FROM octopus_stats WHERE type = 'combiner';
SELECT input_rows, input_bytes, errors FROM octopus_stats WHERE type = 'worker';

CREATE CONTINUOUS VIEW test_octopus_stats0 AS SELECT COUNT(*) FROM test_octopus_stats_stream;
CREATE CONTINUOUS VIEW test_octopus_stats1 AS SELECT COUNT(*) FROM test_octopus_stats_stream;
INSERT INTO test_octopus_stats_stream (x) SELECT generate_series(1, 1000) AS x;

SELECT pg_sleep(2);
SELECT output_rows, errors, cv_create, cv_drop FROM octopus_stats WHERE type = 'combiner';
SELECT input_rows, input_bytes, errors FROM octopus_stats WHERE type = 'worker';

DROP CONTINUOUS VIEW test_octopus_stats0;
DROP CONTINUOUS VIEW test_octopus_stats1;

SELECT pg_sleep(2);
SELECT output_rows, errors, cv_create, cv_drop FROM octopus_stats WHERE type = 'combiner';
SELECT input_rows, input_bytes, errors FROM octopus_stats WHERE type = 'worker';

\c regression
DROP DATABASE octopus_stats_db;
