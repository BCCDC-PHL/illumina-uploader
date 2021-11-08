#!/usr/bin/env python
import json
import os

from invoke import UnexpectedExit
from fabric import task

from .utils import formatStdout, getDateTimeNow, getDateTimeNowIso, convDirToRsyncFormat

@task
def checkupSystemUptime(context, args):
    '''
    Test fabric task to check uptime on remote server
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
def uploadRunToServer(context, args):
    '''
    Rsync correct run directory to correct remote server location
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
    '''
    Create upload_complete.json with updated times in temp location
    SCP upload_complete.json to correct remote server location
    '''
    logger = args["logger"]
    debug = args["debug"]
    for possibleRun in args["runscache"]:
        if args["inFile"] == possibleRun.name:
            actualInDir = possibleRun.inputDir
            actualOutDir = possibleRun.outputDir
    args["inDir"] =  os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
    args["outDir"] = os.path.join(actualOutDir + args["inFile"])
    args["filename"] = "upload_complete.json"
    try:
        #Create upload_complete.json
        createStepString = ""
        now = getDateTimeNowIso()
        upload_complete = {
            "timestamp_start": args["starttime"],
            "timestamp_end": now,
            "input_directory": os.path.join(actualInDir, args["inFile"]),
            "output_directory": args["outDir"],
        }
        upload_complete_json_path = os.path.join(args["inDir"], args["filename"])
        with open(upload_complete_json_path, 'w') as f:
            json.dump(upload_complete, f, indent=2)
            f.write("\n")
        if debug: logger.info("Create upload_complete.json: " + json.dumps(upload_complete))
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
    '''
    Calculate MD5 Hash given directory name. Calculation speed is around 1Gb/Sec
    '''
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
