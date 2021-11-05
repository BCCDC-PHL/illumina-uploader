#!/usr/bin/env python

import argparse
import time
import platform
import sqlite3
import socket

from configparser import ConfigParser
from dataclasses import asdict
from invoke.context import Context

from .database import Database
from .fabfile import checkupSystemUptime, uploadRunToServer, scpUploadCompleteJson
from .utils import setupLogger, addToList, sendEmailUsingPlover, getDateTimeNow, getDateTimeNowIso


def main():
    '''
    Main driver to initialize operations and start watch directory loop
    '''
    parser = argparse.ArgumentParser(description="Scan for new folders in a directory on Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", help="location of config file (default is config.ini)")
    parser.add_argument("--sequencer", help="miseq or nextseq (default taken from config file)")
    parser.add_argument("--upload-single-run", help="location of single folder run to upload (will not update db)")
    parser.add_argument("--create-db", action="store_true", help="initialise sqlite database")
    parser.add_argument("--backup-db", action="store_true", help="backup sqlite database")
    parser.add_argument("--print-db", action="store_true", help="print sqlite database to stdout")
    parser.add_argument("--create-ignorefile", action="store_true", help="create an ignore.txt file based on the current contents of the input directories")
    parser.add_argument("--dry-run", action="store_true", help="mock upload testing without uploading anything [NOT IMPLEMENTED YET]")
    parser.add_argument("--debug", action="store_true", help="print debug data and not send out emails")
    args = parser.parse_args()

    #Initialize objects
    configObject = ConfigParser()
    if not args.config:
        configObject.read("config.ini")    
    else:
        configObject.read(args.config)
    serverInfo = configObject["SERVER"]
    emailInfo = configObject["EMAIL"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]
    context = Context()
    logger = setupLogger(localInfo["logfile"])
    if not args.sequencer:
        sequencer = localInfo["sequencer"]
    else:
        sequencer = args.sequencer
    inputDirs = localInfo["inputDirs"].split(",")
    outputDirs = serverInfo["outputdirs"].split(",")
    inOutMap = dict(zip(inputDirs,outputDirs))
    
    #For Regex matching use https://javascript.info/regexp-quantifiers
    if sequencer == "miseq":
        folderRegex = localInfo["folderregexmiseq"]
    else:
        folderRegex = localInfo["folderregexnextseq"]
    if args.dry_run:
        checkupSystemUptime(context, {"logger":logger})
        logger.info("Dry run completed. Exiting.")
        exit(0)
    isDebug = True if args.debug else False
    single_run = args.upload_single_run
    
    #Database Operations
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = Database(dbInfo, sqlInfo, logger, inputDirs, folderRegex)
    if args.create_db:
        dbObject.createDb()
        exit(0)
    if args.backup_db:
        dbObject.backupDb()
        exit(0)
    if args.print_db:
        dbObject.printDb()
        exit(0)
    if args.create_ignorefile:
        dbObject.createIgnoreFile()
        exit(0)

    try:
        sshformat = commands["sshwincommand"] if platform.system()=="Windows" else commands["sshnixcommand"]
        #Collect rsync command info
        runArgs = {
            "pem": serverInfo["pemfile"],
            "host": serverInfo["host"],
            "login": serverInfo["loginid"],
            "chmod": commands["chmodcommand"],
            "rsync": commands["rsynccommand"],
            "sshformat": sshformat,
            "scp": commands["scpcommand"],
            "logger": logger,
            "debug": isDebug,
        }
        if single_run:
            logger.info("Start One-off run for single directory {0}".format(single_run))
            runArgs["inFile"] = single_run
            dbObject.markFileInDb(single_run, "REUPLOAD")
            logger.info("This process will exit now, and {0} will get picked up by the other illumina-uploader process".format(single_run))
            exit(0)
        else:
            #Call fabric tasks
            while(True):
                logger.info("Start Watching Directores: {0}".format(",".join(inputDirs)))
                #runsCache stores run info for later retrieval. TODO optimize
                runsCache = None
                #Default mail args
                mailArgs = {
                    "debug": isDebug,
                    "token": emailInfo["emailtoken"],
                    "mailto": emailInfo["mailto"]
                }
                try:
                    runsCache = dbObject.watchDirectories(localInfo["watchfilepath"], inOutMap)
                except KeyboardInterrupt as error:
                    reason = "{0}. Network drive needs to be reconnected. Will retry again in {1} minutes".format(error, localInfo["sleeptime"])
                    logger.error(reason)
                    mailArgs["subject"] = emailInfo["mailsubject"].format(status="ERROR"),
                    mailArgs["body"] = emailInfo["mailbody"].format(folderToUpload="cannot be read", status="ERROR", timeOfMail=getDateTimeNow(), reason=reason)
                    if str(emailInfo.get("enabled", None)).lower() == "true":
                        sendEmailUsingPlover(emailInfo["emailurl"], mailArgs, logger)
                foldersToUpload = dbObject.getFolderList()
                if runsCache:
                    for folderName in foldersToUpload:
                        folderToUpload = folderName[0]
                        runArgs["inFile"] = folderToUpload
                        #Mail send before start
                        status = "STARTED"
                        reason = ""
                        mailArgs["subject"] = emailInfo["mailsubject"].format(status=status)
                        mailArgs["body"] = emailInfo["mailbody"].format(folderToUpload=folderToUpload, status=status, timeOfMail=getDateTimeNow(), reason=reason)
                        if str(emailInfo.get("enabled", None)).lower() == 'true':
                            sendEmailUsingPlover(emailInfo["emailurl"], mailArgs, logger)
                        runArgs["runscache"] = runsCache
                        isSuccessful = False
                        runArgs["starttime"] = getDateTimeNowIso()
                        try:
                            isSuccessful = uploadRunToServer(context, runArgs)
                        except (socket.error, OSError) as error:
                            logger.error("Fatal OS / network error: {0}".format(error))
                            reason = "Fatal OS / network error.. will try again in {0} minutes".format(localInfo["sleeptime"])
                        status = "FINISHED" if isSuccessful else "FAILED"
                        logger.info("Marking in DB as {0}".format(status))
                        dbObject.markFileInDb(folderToUpload, status)
                        #Create json file
                        scpUploadCompleteJson(context, runArgs)
                        #Mail send after done, update subject and body
                        mailArgs["subject"] = emailInfo["mailsubject"].format(status=status)
                        mailArgs["body"] = emailInfo["mailbody"].format(folderToUpload=folderToUpload, status=status, timeOfMail=getDateTimeNow(), reason=reason)
                        if str(emailInfo.get("enabled", None)).lower() == 'true':
                            sendEmailUsingPlover(emailInfo["emailurl"], mailArgs, logger)
                #Goto sleep (displayed in minutes)
                logger.info("Sleeping for {0} minutes".format(localInfo["sleeptime"]))
                sleeptimeInSeconds = int(localInfo["sleeptime"])*60
                time.sleep(sleeptimeInSeconds)
    except FileNotFoundError as error:
        logger.info("Shutting down Directory Watch. Exiting.")
    

if __name__ == "__main__":
    main()
