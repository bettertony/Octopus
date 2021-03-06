/*-------------------------------------------------------------------------
 *
 * octopuscmds.h
 *	  prototypes for octopuscmds.c.
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * src/include/commands/octopuscmds.h
 *
 *-------------------------------------------------------------------------
 */

#ifndef PIPELINECMDS_H
#define PIPELINECMDS_H

#include "access/tupdesc.h"
#include "nodes/params.h"
#include "nodes/parsenodes.h"
#include "tcop/dest.h"
#include "tcop/utility.h"
#include "nodes/primnodes.h"

/* guc parameter */
extern int continuous_view_fillfactor;

extern void ExecCreateContViewStmt(CreateContViewStmt *stmt, const char *querystring);
extern void ExecCreateContTransformStmt(CreateContTransformStmt *stmt, const char *querystring);

/* Binary upgrade support */
extern Datum create_cq_set_next_oids_for_matrel(PG_FUNCTION_ARGS);
extern Datum create_cv_set_next_oids_for_seqrel(PG_FUNCTION_ARGS);
extern Datum create_cv_set_next_oids_for_pk_index(PG_FUNCTION_ARGS);
extern Datum create_cv_set_next_oids_for_lookup_index(PG_FUNCTION_ARGS);
extern Datum create_cv_set_next_oids_for_overlay(PG_FUNCTION_ARGS);
extern Datum create_cq_set_next_oids_for_osrel(PG_FUNCTION_ARGS);

#endif   /* PIPELINECMDS_H */
