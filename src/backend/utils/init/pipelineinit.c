/*-------------------------------------------------------------------------
 *
 * octopusinit.c
 *	  routines to support initialization of octopus stuff
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * IDENTIFICATION
 *	  src/backend/utils/init/octopusinit.c
 *
 *-------------------------------------------------------------------------
 */
#include <time.h>
#include <stdlib.h>
#include "postgres.h"

#include "miscadmin.h"
#include "octopus/ipc/microbatch.h"
#include "octopus/analyzer.h"
#include "octopus/planner.h"
#include "octopus/scheduler.h"
#include "octopus/syscache.h"
#include "tcop/utility.h"

/*
 * InitPipeline
 *
 * This is called whenever a new backend is starting up.
 */
void
PipelineShmemInit()
{
	srand(time(NULL) ^ MyProcPid);
	ContQuerySchedulerShmemInit();
	MicrobatchAckShmemInit();
}

/*
 * PipelineInstallHooks
 */
void
PipelineInstallHooks()
{
	InitPipelineSysCache();
	SaveUtilityHook = ProcessUtility_hook;
	ProcessUtility_hook = ProcessUtilityOnContView;
}
