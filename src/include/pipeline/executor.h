/*-------------------------------------------------------------------------
 *
 * executor.h
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * IDENTIFICATION
 *	  src/include/octopus/executor.h
 *
 */
#ifndef CONT_EXECUTE_H
#define CONT_EXECUTE_H

#include "postgres.h"
#include "pg_config.h"

#include "access/htup.h"
#include "access/tupdesc.h"
#include "catalog/octopus_query_fn.h"
#include "executor/tuptable.h"
#include "nodes/bitmapset.h"
#include "nodes/pg_list.h"
#include "pgstat.h"
#include "octopus/scheduler.h"
#include "octopus/ipc/reader.h"
#include "port/atomics.h"
#include "storage/spin.h"
#include "utils/timestamp.h"
#include "utils/tuplestore.h"

typedef struct ContQueryState
{
	Oid query_id;
	ContQuery *query;
	MemoryContext state_cxt;
	MemoryContext tmp_cxt;
	PgStat_StatCQEntryLocal stats;
} ContQueryState;


typedef struct BatchReceiver
{
	Tuplestorestate *buffer;
	void (*flush) (struct BatchReceiver *self, TupleTableSlot *slot);
} BatchReceiver;

typedef struct ContExecutor ContExecutor;
typedef ContQueryState *(*ContQueryStateInit) (ContExecutor *exec, ContQueryState *state);
typedef Relation ContExecutionLock;

struct ContExecutor
{
	MemoryContext cxt;

	ContQueryProcType ptype;
	char *pname;

	Bitmapset *all_queries;
	Bitmapset *exec_queries;

	ipc_tuple_reader_batch *batch;

	Oid curr_query_id;
	ContQueryState *curr_query;
	ContQueryState *states[MAX_CQS];
	ContQueryStateInit initfn;
	ContExecutionLock lock;
};

extern Oid PipelineExecLockRelationOid;

extern ContExecutor *ContExecutorNew(ContQueryStateInit initfn);
extern void ContExecutorDestroy(ContExecutor *exec);
extern void ContExecutorStartBatch(ContExecutor *exec, int timeout);
extern Oid ContExecutorStartNextQuery(ContExecutor *exec, int timeout);
extern void ContExecutorPurgeQuery(ContExecutor *exec);
extern void *ContExecutorIterate(ContExecutor *exec, int *len);
extern void ContExecutorEndQuery(ContExecutor *exec);
extern void ContExecutorEndBatch(ContExecutor *exec, bool commit);
extern void ContExecutorAbortQuery(ContExecutor *exec);
extern ContExecutionLock AcquireContExecutionLock(LOCKMODE mode);
extern void ReleaseContExecutionLock(ContExecutionLock rel);

#endif
