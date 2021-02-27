#!/usr/bin/env python
import argparse, platform, sqlite3, time
from fabfile import rsyncFolder, checkupSystemUptime
from invoke.context import Context
from configparser import ConfigParser
from utils import setupLogger, addToList, sendEmailUsingPlover, getDateTimeNow
from database import Database

def main(args):
    '''
    Main driver to initialize operations and start watch directory loop
    '''
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
    inputdirs = localInfo["inputdirs"].split(",")

    #Check arguments
    if sequencer == "miseq":
        folderRegex = localInfo["folderregexmiseq"]
    else:
        folderRegex = localInfo["folderregexnextseq"]
    if args.dry_run:
        checkupSystemUptime(context, {"logger":logger})
        logger.info("Dry run completed. Exiting.")
        exit(0)
    isDebug = True if args.debug else False

    #Database Operations
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = Database(dbInfo, sqlInfo, logger, inputdirs, folderRegex)
    if args.create_db:
        dbObject.createDb()
        exit(0)
    if args.backup_db:
        dbObject.backupDb()
        exit(0)

    try:
        while(True):
            sshformat = commands["sshwincommand"] if platform.system()=="Windows" else commands["sshnixcommand"]
            #Collect rsync command info
            runargs = {
                "pem": serverInfo["pemfile"],
                "host": serverInfo["host"],
                "login": serverInfo["loginid"],
                "outDir": serverInfo["outputdir"],
                "chmod": commands["chmodcommand"],
                "rsync": commands["rsynccommand"],
                "sshformat": sshformat,
                "scp": commands["scpcommand"],
                "mailmessage": localInfo["mailmessage"],
                "logger": logger,
                "debug": isDebug
            }
            #Call rsync
            if args.upload_single_run:
                logger.info("Start One-off run for single directory {0}".format(args.upload_single_run))
                runargs["inFile"] = args.upload_single_run
                rsyncFolder(context, runargs)
                addToList(inputdirs, args.upload_single_run, "ignore.txt")
                logger.info("Folder {0} added to ignore list".format(args.upload_single_run))
                break
            else:
                logger.info("Start Watching Directory..")
                dbObject.watchDirectories(localInfo["watchfilepath"])
                foldersToUpload = dbObject.getFolderList()
                for folderName in foldersToUpload:
                    runargs["inDir"] = dbObject.findFolder(folderName[0])
                    if isDebug: logger.info("{0} found in {1}".format(folderName[0], runargs["inDir"]))
                    runargs["inFile"] = folderName[0]
                    isSuccessful = rsyncFolder(context, runargs)
                    if isSuccessful:
                        dbObject.markFileInDb(folderName[0], "UPLOADED")
                        args = {
                            "token": emailInfo["emailtoken"],
                            "mailto": emailInfo["mailto"],
                            "subject": "Folder {0} successfully uploaded to sabin".format(folderName[0]),
                            "body": "Time of upload {0}".format(getDateTimeNow()),
                            }
                        sendEmailUsingPlover(emailInfo["emailurl"], args)
                    else:
                         logger.info("Unsuccessful upload, marking in DB as FAILED")
                         dbObject.markFileInDb(folderName[0], "FAILED")
            #Goto sleep (displayed in minutes)
            logger.info("Sleeping for {0} minutes".format(localInfo["sleeptime"]))
            sleeptimeInSeconds = int(localInfo["sleeptime"])*60
            time.sleep(sleeptimeInSeconds)
    except KeyboardInterrupt as error:
            logger.info("Shutting down Directory Watch. Exiting.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for new folders in a directory on Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", help="location of config file (default is config.ini)")
    parser.add_argument("--sequencer", help="miseq or nextseq (default taken from config file")
    parser.add_argument("--upload-single-run", help="location of single folder run to upload (will not update db)")
    parser.add_argument("--create-db", action="store_true", help="initialise sqlite database")
    parser.add_argument("--backup-db", action="store_true", help="backup sqlite database")
    parser.add_argument("--dry-run", action="store_true", help="mock upload testing without uploading anything")
    parser.add_argument("--debug", action="store_true", help="print debug data that should aid in problem solving")
    args = parser.parse_args()
    main(args)
