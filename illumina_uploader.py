#!/usr/bin/env python
import argparse, platform, sqlite3
from fabfile import rsyncFolder
from invoke.context import Context
from configparser import ConfigParser
from utils import database

def main(args):
    #Initialize objects
    configObject = ConfigParser()
    configObject.read(args.config)
    serverInfo = configObject["SERVER"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]
    context = Context()

    #Check arguments
    if args.sequencer == "miseq":
        folderRegex = localInfo["folderregexmiseq"]
    else:
        folderRegex = localInfo["folderregexnextseq"]

    #Connect to Database
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = database(dbInfo, sqlInfo)
    if args.create_db:
        dbObject.createDb()

    if args.upload_folder:
        dbObject.prepFolders(localInfo["inputdir"], folderRegex, args.upload_folder)
    elif args.scan_directory:
        dbObject.prepFolders(localInfo["inputdir"], folderRegex, None)
    else:
        print("Resuming from database")

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
    parser = argparse.ArgumentParser(description="Watch for new files in Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", required=True, help="location of config file")
    parser.add_argument("--sequencer", required=True, help="miseq or nextseq")
    parser.add_argument("--upload-folder", help="location of single folder to upload")
    parser.add_argument("--scan-directory", action="store_true", help="scan directory specified in config file")
    parser.add_argument("--pem-file", help="location of pem file")
    parser.add_argument("--create-db", action="store_true", help="initialise sqlite database")
    parser.add_argument("--backup-db", action="store_true", help="backup sqlite database")
    parser.add_argument("--dry-run", action="store_true", help="mock upload testing without uploading anything")
    args = parser.parse_args()
    main(args)
