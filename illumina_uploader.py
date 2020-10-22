#!/usr/bin/env python
import argparse, platform
from fabfile import rsyncFolder
from invoke.context import Context
from configparser import ConfigParser
from utils import database

def main(args):
    configObject = ConfigParser()
    configObject.read(args.config_file)

    #Connect to Database
    dbInfo = configObject["DB"]
    sqlInfo = configObject["SQL"]
    dbObject = database(dbInfo, sqlInfo)
    if args.create_db: dbObject.createDb()
    
    if args.upload_single_folder:
        folderList = dbObject.addToFolderList(args.upload_single_folder)
    else:
        folderList = dbObject.getFolderList()
    
    serverInfo = configObject["SERVER"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]

    #Check system
    sshcommand = commands["sshwincommand"] if platform.system()=="Windows" else commands["sshnixcommand"]
    
    #Collect rsync command info
    runargs = {
        "pem": serverInfo["pemfile"],
        "host": serverInfo["host"],
        "login":serverInfo["loginid"],
        "outDir":serverInfo["outputdir"],
        "inDir":localInfo["inputdir"],
        "inFile":args.upload_single_folder, #TODO: TEMP
        "chmod":commands["chmodcommand"],
        "rsync":commands["rsynccommand"],
        "sshcommand":sshcommand,
    }
    context = Context()
    rsyncFolder(context, runargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grab and push miseq analysis to plover.")
    parser.add_argument("--config_file", dest="config_file", required=True)
    parser.add_argument("--upload_single_folder", dest="upload_single_folder", required=True)
    parser.add_argument("--create_db", action="store_true")
    args = parser.parse_args()
    main(args)
