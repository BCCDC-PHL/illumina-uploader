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
    #Checksum Calc (6 Sec / 6 GB)
    #find . -xdev -type f -print0 | LC_COLLATE=C sort -z | xargs -0 tail -qc100 | md5sum -
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
    copyfilename = args["inDir"] + args["inFile"] + "/COPY_COMPLETE"
    try:
        if debug: logger.info("Running #1: rsync "+args["rsync"].format_map(args))
        #STEP 1: rsync run directory
        result = context.run("rsync "+args["rsync"].format_map(args))
        #STEP 2: create COPY_COMPLETE file
        catcommand = "echo {0} > {1}".format(F"{datetime.now():%Y-%m-%d %H:%M:%S}", copyfilename)
        if debug: logger.info("Running #2: "+catcommand)
        result = context.run(catcommand)
        #STEP 3: rsync COPY_COMPLETE file
        if debug: logger.info("Running #3: rsync "+args["rsync"].format_map(args))
        result = context.run("rsync "+args["rsync"].format_map(args))
    except UnexpectedExit as error:
        logger.info("Interrupted!")
        logger.info(error)
        logger.info("Exiting!")
    else:
        logger.info("Please wait.. writing logfile (might take a while)")
        formatStdout(result, logger)
        if debug: logger.info("Completed!")

@task
def scpCopyMailFile(context, args):
    logger = args["logger"]
    debug = args["debug"]
    args["inDir"] = args["inDir"] + "mail/"
    args["outDir"] = args["outDir"] + "mail/"
    args["uploadTime"] = F"{datetime.now():%Y_%m_%d_%H_%M_%S}"
    args["filename"] = "msg_{0}.txt".format(args["uploadTime"])
    try:
        createcommand = "echo {0} > {1}{2}".format(args["mailmessage"].format_map(args), args["inDir"], args["filename"])
        copycommand = args["scp"].format_map(args)
        if debug:
            logger.info("Running create command")
            logger.info(createcommand)
            logger.info("Running scp command")
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