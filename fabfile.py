#!/usr/bin/env python
from invoke import UnexpectedExit
from fabric import task
from utils import formatStdout

@task
def checkupSystemUptime(context, args):
    '''
    Test fabric task
    '''
    logger = args["logger"]
    try:
        logger.info("Running: uptime")
        result = context.run("uptime")
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        formatStdout(result, logger)
        logger.info("Completed: uptime")

@task
def rsyncFolder(context, args):
    '''
    Rsync fabric task.
    TODO check performance when writing result to logfile
    '''
    logger = args["logger"]
    try:
        #logger.info("Running: rsync "+args["rsync"].format_map(args))
        result = context.run("rsync "+args["rsync"].format_map(args))
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        logger.info("Please wait.. writing logfile (might take a while)")
        formatStdout(result, logger)
        #logger.info("Completed: rsync "+args["rsync"].format_map(args))

@task
def putCopyCompleteFile(context, args):
    #COPY_COMPLETE.txt with time stamp
    logger = args["logger"]
    try:
        logger.info("Running: touch COPY_COMPLETE.TXT")
        result = context.run("touch COPY_COMPLETE.TXT")
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        formatStdout(result, logger)
        logger.info("Completed: touch COPY_COMPLETE.TXT")

@task
def putMailFile(context, args):
    #RUN_ERROR
    # 6 sec:  find . -xdev -type f -print0 | LC_COLLATE=C sort -z | xargs -0 tail -qc100 | md5sum -
    logger = args["logger"]
    try:
        logger.info("Running: mkdir Mail")
        result = context.run("mkdir Mail")
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        formatStdout(result, logger)
        logger.info("Completed: mkdir Mail")