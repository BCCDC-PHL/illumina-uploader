#!/usr/bin/env python
import argparse, platform, sqlite3, time
from fabfile import rsyncFolder, checkupSystemUptime
from invoke.context import Context
from configparser import ConfigParser
from utils import Database, setupLogger

def main(args):
    '''
    Main driver to initialize operations and start watch directory loop
    '''
    #Initialize objects
    configObject = ConfigParser()
    configObject.read(args.config)
    serverInfo = configObject["SERVER"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]
    context = Context()
    
    #Setup logger
    logger = setupLogger(localInfo["logfile"])

    #Check arguments
    if args.sequencer == "miseq":
        folderRegex = localInfo["folderregexmiseq"]
    else:
        folderRegex = localInfo["folderregexnextseq"]
    if args.dry_run:
        checkupSystemUptime(context, {"logger":logger})
        logger.info("Dry run completed. Exiting.")
        exit(0)

    #Database Operations
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = Database(dbInfo, sqlInfo, logger)
    if args.create_db:
        dbObject.createDb()
        exit(0)
    if args.backup_db:
        dbObject.backupDb()
        exit(0)

    try:
        logger.info("Start Watching Directory..")
        sleeptime = int(localInfo["sleeptime"])*60 #In Minutes
        while(True):
            sshcommand = commands["sshwincommand"] if platform.system()=="Windows" else commands["sshnixcommand"]
            
            #Collect rsync command info
            runargs = {
                "pem": serverInfo["pemfile"],
                "host": serverInfo["host"],
                "login":serverInfo["loginid"],
                "outDir":serverInfo["outputdir"],
                "inDir":localInfo["inputdir"],
                "chmod":commands["chmodcommand"],
                "rsync":commands["rsynccommand"],
                "sshcommand":sshcommand,
                "logger":logger,
            }

            #Call rsync
            if args.upload_single_run:
                runargs["inFile"] = args.upload_single_run
                rsyncFolder(context, runargs)
                break
            else:
                dbObject.watchDirectory(localInfo["inputdir"], folderRegex, localInfo["watchfilepath"])
                foldersToUpload = dbObject.getFolderList()
                for rsyncfolder in foldersToUpload:
                    runargs["inFile"] = rsyncfolder[0]
                    rsyncFolder(context, runargs)
            
            logger.info("Sleeping for {0} seconds".format(sleeptime))
            time.sleep(sleeptime)
    except KeyboardInterrupt as error:
            logger.info("Shutting down Directory Watch. Exiting.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for new folders in a directory on Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", required=True, help="location of config file")
    parser.add_argument("--sequencer", required=True, help="miseq or nextseq")
    parser.add_argument("--upload-single-run", help="location of single folder run to upload (will not update db)")
    parser.add_argument("--pem-file", help="location of pem file")
    parser.add_argument("--create-db", action="store_true", help="initialise sqlite database")
    parser.add_argument("--backup-db", action="store_true", help="backup sqlite database")
    parser.add_argument("--dry-run", action="store_true", help="mock upload testing without uploading anything")
    args = parser.parse_args()
    main(args)
