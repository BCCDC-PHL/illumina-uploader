#!/usr/bin/env python
import argparse, platform, sqlite3
from fabfile import rsyncFolder, checkupSystemUptime
from invoke.context import Context
from configparser import ConfigParser
from utils import Database, setupLogger

def main(args):
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
        exit(0)

    #Database Operations
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = Database(dbInfo, sqlInfo, logger)
    if args.create_db:
        dbObject.createDb()
    if args.backup_db:
        dbObject.backupDb()

    #Start Watching Directory
    print(dbObject.watchDirectory(localInfo["inputdir"], folderRegex, localInfo["watchfilepath"], localInfo["sleeptime"]))
    exit(0)
    
    if args.upload_single_run:
        dbObject.prepFolders(localInfo["inputdir"], folderRegex, args.upload_folder)
    elif args.resume:
        logger.info("Resuming from database")
    else:
        dbObject.prepFolders(localInfo["inputdir"], folderRegex, None)

    #Check system
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
    if args.upload_folder:
        runargs["inFile"] = args.upload_folder
        rsyncFolder(context, runargs)
    else:
        foldersToUpload = dbObject.getFolderList()
        for rsyncfolder in foldersToUpload:
            runargs["inFile"] = rsyncfolder[0]
            rsyncFolder(context, runargs)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for new folders in a directory on Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", required=True, help="location of config file")
    parser.add_argument("--sequencer", required=True, help="miseq or nextseq")
    parser.add_argument("--upload-single-run", help="location of single folder run to upload")
    parser.add_argument("--resume", action="store_true", help="resume uploading from database, skip scan directory")
    parser.add_argument("--pem-file", help="location of pem file")
    parser.add_argument("--create-db", action="store_true", help="initialise sqlite database")
    parser.add_argument("--backup-db", action="store_true", help="backup sqlite database")
    parser.add_argument("--dry-run", action="store_true", help="mock upload testing without uploading anything")
    args = parser.parse_args()
    main(args)
