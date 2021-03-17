#!/usr/bin/env python
from invoke import UnexpectedExit
from fabric import task
from utils import formatStdout, getDateTimeNow, getDateTimeNowIso, convDirToRsyncFormat

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
def uploadRunToSabin(context, args):
    '''
    Rsync fabric task
    '''
    #Get inDir and outDir from runsCache
    for possibleRun in args["runscache"]:
        if args["inFile"] == possibleRun.name:
            args["inDir"] = possibleRun.inputDir
            args["outDir"] = possibleRun.outputDir
    
    logger = args["logger"]
    debug = args["debug"]
    args["inDir"] = convDirToRsyncFormat(args["inDir"])
    try:
        #rsync run directory
        rsyncStep = args["rsync"].format_map(args)
        if debug: logger.info("Running rsyncFolder run directory: "+rsyncStep)
        result = context.run(rsyncStep)
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
        return False
    else:
        logger.info("Please wait.. writing logfile")
        formatStdout(result, logger)
        return True

@task
def scpUploadCompleteJson(context, args):
    logger = args["logger"]
    debug = args["debug"]
    for possibleRun in args["runscache"]:
        if args["inFile"] == possibleRun.name:
            args["outDir"] = possibleRun.outputDir
    args["inDir"] = "temp/"
    args["outDir"] = args["outDir"] + args["inFile"] + "/"
    args["filename"] = "upload_complete.json" #Where illumina-uploader is run from
    try:
        #Create upload_complete.json
        createStep = "echo {{\"timestamp_start\":\"{0}\",\"timestamp_end\":\"{1}\"}} > {2}".format(args["starttime"], getDateTimeNowIso(), args["inDir"]+args["filename"])
        if debug: logger.info("Create upload_complete.json: "+createStep)
        result = context.run(createStep)
        #SCP upload_complete.json
        scpStep = args["scp"].format_map(args)
        if debug: logger.info("SCP upload_complete.json: "+scpStep)
        result = context.run(scpStep)
    except (UnexpectedExit, KeyboardInterrupt) as error:
        logger.info("Interrupted!")
        logger.info(error)
        return False
    else:
        logger.info("Please wait.. writing logfile")
        formatStdout(result, logger)
        return True

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
