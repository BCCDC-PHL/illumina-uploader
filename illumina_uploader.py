#!/usr/bin/env python
import argparse, platform
from fabfile import rsyncFolder
from invoke.context import Context
from configparser import ConfigParser

def main(args):
    configObject = ConfigParser()
    configObject.read(args.config_file)

    serverInfo = configObject["SERVER"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]
    
    pem = serverInfo["pemfile"]
    host = serverInfo["host"]
    login = serverInfo["loginid"]
    outDir = serverInfo["outputdir"]

    inDir = localInfo["inputdir"]
    
    chmod = commands["chmodcommand"]
    rsync = commands["rsynccommand"]

    if platform.system()=="Windows":
        sshcommand = commands["sshwincommand"]
    else:
        sshcommand = commands["sshnixcommand"]
    
    runargs = {
        "pem": pem,
        "host": host,
        "login":login,
        "outDir":outDir,
        "inDir":inDir,
        "inFile":args.upload_single_folder,
        "chmod":chmod,
        "rsync":rsync,
        "sshcommand":sshcommand,
    }
    context = Context()
    rsyncFolder(context, runargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grab and push miseq analysis to plover.")
    parser.add_argument("--config_file", dest="config_file", required=True)
    parser.add_argument("--upload_single_folder", dest="upload_single_folder", required=True)
    args = parser.parse_args()
    main(args)
