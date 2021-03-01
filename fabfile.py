#!/usr/bin/env python
from invoke import UnexpectedExit
from fabric import task
from utils import formatStdout, getDateTimeNow, convDirToRsyncFormat

@task
def checkupSystemUptime(context, args):
    '''
    Test fabric task
    '''
    logger = args["logger"]
    try:
        logger.info("Running: uptime")
        result = context.run("uptime")
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
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
    args["inDir"] = convDirToRsyncFormat(args["inDir"])
    try:
        #STEP 1: rsync run directory
        step1 = args["rsync"].format_map(args)
        if debug: logger.info("Running rsyncFolder run directory: "+step1)
        result = context.run(step1)
        #STEP 2: create COPY_COMPLETE file
        step2 = "echo {0} > {1}".format(getDateTimeNow(), copyfilename)
        if debug: logger.info("Running rsyncFolder create COPY_COMPLETE file: "+step2)
        result = context.run(step2)
        #STEP 3: rsync COPY_COMPLETE file
        step3 = args["rsync"].format_map(args)
        if debug: logger.info("Running rsyncFolder rsync COPY_COMPLETE file: "+step3)
        result = context.run(step3)
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
        return False
    else:
        logger.info("Please wait.. writing logfile")
        formatStdout(result, logger)
        return True

'''
@task
def scpCopyMailFile(context, args):
    logger = args["logger"]
    debug = args["debug"]
    args["inDir"] = args["inDir"] + "mail/"
    args["outDir"] = args["outDir"] + "mail/"
    args["uploadTime"] = getDateTimeNow()
    args["filename"] = "msg_{0}.txt".format(args["uploadTime"])
    try:
        createcommand = "echo {0} > {1}{2}".format(args["mailmessage"].format_map(args), args["inDir"], args["filename"])
        copycommand = args["scp"].format_map(args)
        if debug: logger.info("Running scpCopyMailFile create command: "+createcommand)
        result = context.run(copycommand)
        if debug: logger.info("Running scpCopyMailFile scp command: "+copycommand)
        result = context.run(createcommand)
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
    else:
        formatStdout(result, logger)
        if debug: logger.info("Completed!")

@task
def calcMD5Hash(context, args):
    # Calculate MD5 Hash given directory name. Calculation speed is 1Gb/Sec
    logger = args["logger"]
    try:
        logger.info("Running: calcMD5Hash")
        result = context.run("find . -xdev -type f -print0 | LC_COLLATE=C sort -z | xargs -0 tail -qc100 | md5sum -")
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
    else:
        formatStdout(result, logger)
        logger.info("Completed: calcMD5Hash")

'''