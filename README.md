# Octopus
Streaming Analytics & Pattern Event Processing Platform

## Building from source
Install some dependencies first:
```
sudo apt-get install libreadline6 libreadline6-dev g++ flex bison python-pip pkgconf zlib1g-dev python-dev libpq-dev
sudo pip install -r src/test/py/requirements.txt
```

Next you'll have to install [ZeroMQ](http://zeromq.org/) which Octopus uses for inter-process communication. [Here's](https://gist.github.com/usmanm/32a54a6b0f1f29d7737f86e29f837afa) a gist with instructions to build and install ZeroMQ from source.

#### Build the Octopus core (with debug symbols)
```
./configure CFLAGS="-g -O0" --enable-cassert --prefix=</path/to/dev/installation>
make
make install
```

#### Add your dev installation path to the PATH environment variable
```
export PATH=/path/to/dev/installation/bin:$PATH
```

#### Test Octopus *(optional)*
Run the following command:

```
make check
```

#### Bootstrap the Octopus environment
Create Octopus's physical data directories, configuration files, etc:

```
make bootstrap
```

**`make bootstrap` only needs to be run the first time you install Octopus**. The resources that `make bootstrap` creates may continue to be used as you change and rebuild Octopus.


#### Run Octopus
Run all of the daemons necessary for Octopus to operate:

```
make run
```

Enter `Ctrl+C` to shut down Octopus.

`make run` uses the binaries in the Octopus source root compiled by `make`, so you don't need to `make install` before running `make run` after code changes--only `make` needs to be run.

The basic development flow is:

```
make
make run
^C

# Make some code changes...
make
make run
```

#### Send Octopus some data

Now let's generate some test data and stream it into a simple continuous view. First, create the stream and the continuous view that reads from it:

    octopus
    =# CREATE STREAM test_stream (key integer, value integer);
    CREATE STREAM
    =# CREATE CONTINUOUS VIEW test_view AS SELECT key, COUNT(*) FROM test_stream GROUP BY key;
    CREATE CONTINUOUS VIEW

Events can be emitted to Octopus streams using regular SQL `INSERTS`. Any `INSERT` target that isn't a table is considered a stream by Octopus, meaning streams don't need to have a schema created in advance. Let's emit a single event into the `test_stream` stream since our continuous view is reading from it:

    octopus
    =# INSERT INTO test_stream (key, value) VALUES (0, 42);
    INSERT 0 1

The 1 in the `INSERT 0 1` response means that 1 event was emitted into a stream that is actually being read by a continuous query. Now let's insert some random data:

    =# INSERT INTO test_stream (key, value) SELECT random() * 10, random() * 10 FROM generate_series(1, 100000);
    INSERT 0 100000

Query the continuous view to verify that the continuous view was properly updated. Were there actually 100,001 events counted?

    octopus -c "SELECT sum(count) FROM test_view"
      sum
    -------
    100001
    (1 row)

What were the 10 most common randomly generated keys?

    octopus -c "SELECT * FROM test_view ORDER BY count DESC limit 10"
	key  | count 
	-----+-------
	 2   | 10124
	 8   | 10100
	 1   | 10042
	 7   |  9996
	 4   |  9991
	 5   |  9977
	 3   |  9963
	 6   |  9927
	 9   |  9915
	10   |  4997
	 0   |  4969

	(11 rows)
