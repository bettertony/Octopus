/*
 * psql - the PostgreSQL interactive terminal
 *
 * Support for Octopus commands
 *
 * Copyright (c) 2013-2015, Octopus
 *
 * src/bin/psql/octopus.c
 */
#include "postgres_fe.h"

#include <ctype.h>

#include "common.h"
#include "dumputils.h"
#include "settings.h"
#include "octopus.h"

/*
 * \zq
 *
 * List all continuous views
 */
extern bool
listContinuousViews(void)
{

	PQExpBufferData buf;
	PGresult   *res;
	printQueryOpt myopt = pset.popt;

	initPQExpBuffer(&buf);
	printfPQExpBuffer(&buf,	"SELECT * FROM octopus_views()");

	res = PSQLexec(buf.data);
	termPQExpBuffer(&buf);
	if (!res)
		return false;

	if (PQntuples(res) == 0 && !pset.quiet)
	{
		fprintf(pset.queryFout, _("No continuous views found.\n"));
	}
	else
	{
		myopt.nullPrint = NULL;
		myopt.title = _("List of continuous views");
		myopt.translate_header = true;

		printQuery(res, &myopt, pset.queryFout, false, pset.logfile);
	}

	PQclear(res);
	return true;
}

/*
 * \X
 *
 * List all continuous transforms
 */
extern bool
listContinuousTransforms(void)
{

	PQExpBufferData buf;
	PGresult   *res;
	printQueryOpt myopt = pset.popt;

	initPQExpBuffer(&buf);
	printfPQExpBuffer(&buf,	"SELECT * FROM octopus_transforms()");

	res = PSQLexec(buf.data);
	termPQExpBuffer(&buf);
	if (!res)
		return false;

	if (PQntuples(res) == 0 && !pset.quiet)
	{
		fprintf(pset.queryFout, _("No continuous transforms found.\n"));
	}
	else
	{
		myopt.nullPrint = NULL;
		myopt.title = _("List of continuous transforms");
		myopt.translate_header = true;

		printQuery(res, &myopt, pset.queryFout, false, pset.logfile);
	}

	PQclear(res);
	return true;
}
