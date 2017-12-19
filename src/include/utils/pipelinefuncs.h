/*-------------------------------------------------------------------------
 *
 * octopusfuncs.h
 *
 *	  Interface for Octopus functions
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * IDENTIFICATION
 *	  src/backend/utils/octopusfuncs.h
 *
 *-------------------------------------------------------------------------
 */
#ifndef PIPELINEFUNCS_H
#define PIPELINEFUNCS_H


#define DISPLAY_OVERLAY_VIEW -2

/* continuous query process stats */
extern Datum cq_proc_stat_get(PG_FUNCTION_ARGS);

/* continuous query stats */
extern Datum cq_stat_get(PG_FUNCTION_ARGS);

/* stream stats */
extern Datum stream_stat_get(PG_FUNCTION_ARGS);

/* octopus views */
extern Datum octopus_views(PG_FUNCTION_ARGS);

/* octopus transforms */
extern Datum octopus_transforms(PG_FUNCTION_ARGS);

/* octopus streams */
extern Datum octopus_streams(PG_FUNCTION_ARGS);

/* global octopus stats */
extern Datum octopus_stat_get(PG_FUNCTION_ARGS);

/* matrel overlay view definition */
extern Datum octopus_get_overlay_viewdef(PG_FUNCTION_ARGS);

/* Octopus version string */
extern Datum octopus_version(PG_FUNCTION_ARGS);

extern Datum octopus_get_worker_querydef(PG_FUNCTION_ARGS);

extern Datum octopus_get_combiner_querydef(PG_FUNCTION_ARGS);

extern Datum octopus_combine_table(PG_FUNCTION_ARGS);

extern Datum json_object_int_sum_transfn(PG_FUNCTION_ARGS);

extern Datum json_object_int_sum_transout(PG_FUNCTION_ARGS);

extern Datum octopus_flush(PG_FUNCTION_ARGS);

extern Datum set_ttl(PG_FUNCTION_ARGS);

extern Datum ttl_expire(PG_FUNCTION_ARGS);

extern Datum activate(PG_FUNCTION_ARGS);

extern Datum deactivate(PG_FUNCTION_ARGS);

extern Datum truncate_continuous_view(PG_FUNCTION_ARGS);

#endif
