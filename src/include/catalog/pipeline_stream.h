/*-------------------------------------------------------------------------
 *
 * octopus_stream.h
 *		Definition of the octopus_stream catalog table
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * src/include/catalog/octopus_stream.h
 *
 *-------------------------------------------------------------------------
 */
#ifndef PIPELINE_STREAM_H
#define PIPELINE_STREAM_H

#include "catalog/genbki.h"

#define PipelineStreamRelationId  4249

extern Oid PipelineStreamRelationOid;


/* ----------------------------------------------------------------
 * ----------------------------------------------------------------
 */
CATALOG(octopus_stream,4249)
{
	Oid relid;
#ifdef CATALOG_VARLEN
	bytea queries;
#endif
} FormData_octopus_stream;

typedef FormData_octopus_stream *Form_octopus_stream;

#define Natts_octopus_stream			2
#define Anum_octopus_stream_relid		1
#define Anum_octopus_stream_queries 	2

#endif
