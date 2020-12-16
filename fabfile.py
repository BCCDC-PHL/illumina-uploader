#!/usr/bin/env python
from fabric import task

@task
def checkupSystemUptime(context, args):
    logger = args["logger"]
    logger.info("Running: uptime")
    stdout = context.run("uptime")
    logger.info("Completed: uptime")

@task
def rsyncFolder(context, args):
    logger = args["logger"]
    logger.info("Running: rsync "+args["rsync"].format_map(args))
    context.run("rsync "+args["rsync"].format_map(args))
    logger.info("Completed: rsync "+args["rsync"].format_map(args))
