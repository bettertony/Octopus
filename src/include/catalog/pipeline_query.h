/*-------------------------------------------------------------------------
 *
 * octopus_query.h
 *	  definition of continuous queries that have been registered
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * src/include/catalog/octopus_query.h
 *
 * NOTES
 *	  the genbki.pl script reads this file and generates .bki
 *	  information from the DATA() statements.
 *
 *-------------------------------------------------------------------------
 */
#ifndef PIPELINE_QUERY_H
#define PIPELINE_QUERY_H

#include "catalog/genbki.h"
#include "datatype/timestamp.h"

/* ----------------------------------------------------------------
 *		octopus_query definition.
 *
 *		cpp turns this into typedef struct FormData_octopus_query
 * ----------------------------------------------------------------
 */
#define PipelineQueryRelationId  4242

extern Oid PipelineQueryRelationOid;

CATALOG(octopus_query,4242)
{
	int32		id;
	char 		type;
	Oid			relid;
	bool 		active;
	Oid 		osrelid;

	/* valid for views only */
	Oid			matrelid;
	Oid  	  seqrelid;
	Oid  	  pkidxid;
	Oid 	  lookupidxid;
	int16	step_factor;
	int32		ttl;
	int16		ttl_attno;

	/* valid for transforms only */
	Oid			tgfn;
	int16		tgnargs;

#ifdef CATALOG_VARLEN
	bytea       tgargs;
	text		query;
#endif
} FormData_octopus_query;

/* ----------------
 *		Form_octopus_query corresponds to a pointer to a tuple with
 *		the format of the octopus_query relation.
 * ----------------
 */
typedef FormData_octopus_query *Form_octopus_query;

/* ----------------
 *		compiler constants for octopus_query
 * ----------------
 */
#define Natts_octopus_query             16
#define Anum_octopus_query_id           1
#define Anum_octopus_query_type         2
#define Anum_octopus_query_relid	     3
#define Anum_octopus_query_active       4
#define Anum_octopus_query_osrelid	     5
#define Anum_octopus_query_matrelid     6
#define Anum_octopus_query_seqrelid     7
#define Anum_octopus_query_pkidxid      8
#define Anum_octopus_query_lookupidxid  9
#define Anum_octopus_query_step_factor  10
#define Anum_octopus_query_ttl  		 11
#define Anum_octopus_query_ttl_attno  	 12
#define Anum_octopus_query_tgfn         13
#define Anum_octopus_query_tgnargs	     14
#define Anum_octopus_query_tgargs       15
#define Anum_octopus_query_query        16

#define PIPELINE_QUERY_VIEW 		'v'
#define PIPELINE_QUERY_TRANSFORM 	't'

#endif   /* PIPELINE_QUERIES_H */
