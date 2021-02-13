#!/usr/bin/env python
from invoke import UnexpectedExit
from fabric import task
from utils import formatStdout
from datetime import datetime

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
    debug = args["debug"]
    try:
        if debug: logger.info("Running: rsync "+args["rsync"].format_map(args))
        result = context.run("rsync "+args["rsync"].format_map(args))
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        logger.info("Please wait.. writing logfile (might take a while)")
        formatStdout(result, logger)
        if debug: logger.info("Completed: rsync "+args["rsync"].format_map(args))

@task
def scpCopyCompleteFile(context, args):
    logger = args["logger"]
    debug = args["debug"]
    copyfilepath = args["inDir"] + args["inFile"] + "/"
    try:
        createcommand = F"echo {datetime.now():%Y-%m-%d %H:%M:%S} > {copyfilepath}COPY_COMPLETE"
        copycommand = args["scp"].format_map(args)
        if debug:
            logger.info("Running both create and copy commands")
            logger.info(createcommand)
            logger.info(copycommand)
        result = context.run(createcommand)
        result = context.run(copycommand)
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        formatStdout(result, logger)
        if debug:
            logger.info("Completed!")
            logger.info(createcommand)
            logger.info(copycommand)

@task
def putMailFile(context, args):
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