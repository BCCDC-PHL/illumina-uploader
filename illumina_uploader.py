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


    #Connect to Database
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = database(dbInfo, sqlInfo)
    if args.create_db:
        dbObject.createDb()

    if args.upload_folder or args.scan_directory:
        try:
            dbObject.addToFolderList(args.upload_folder, localInfo["folderregex"], localInfo["inputdir"])
        except sqlite3.OperationalError as error:
            print("DB error: {0}".format(error))
    else:
        print("Need either upload-folder or scan-directory argument")
        exit(0)

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
    
    #Get folders to upload
    foldersToUpload = dbObject.getFolderList()

    #Call rsync
    if args.upload_single_folder:
        runargs["inFile"] = args.upload_single_folder
        rsyncFolder(context, runargs)
    else:
        for rsyncfolder in foldersToUpload:
            runargs["inFile"] = rsyncfolder[0]
            rsyncFolder(context, runargs)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch for new files in Illumina sequencer and upload to remote server.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--upload-folder")
    parser.add_argument("--scan-directory")
    parser.add_argument("--pem-file")
    parser.add_argument("--create-db", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(args)
    main(args)
