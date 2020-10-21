#!/usr/bin/env python

from fabric import task
from configparser import ConfigParser
import platform

configObject = ConfigParser()
configObject.read("config.ini")

@task
def checkupSystemUptime(context):
    context.run("uptime")

@task
def rsyncFolders(context):
    serverInfo = configObject["SERVER"]
    localInfo = configObject["LOCAL"]
    commands = configObject["COMMANDS"]
    
    pem = serverInfo["pemfile"]
    host = serverInfo["host"]
    loginid = serverInfo["loginid"]
    outDir = serverInfo["outputdir"]

    inDir = localInfo["inputdir"]
    inFile = localInfo["filename"]
    
    chmod = commands["chmodcommand"]
    rsync = commands["rsynccommand"]

    if platform.system()=="Windows":
        sshcommand = commands["sshwincommand"]
    else:
        sshcommand = commands["sshnixcommand"]
    print("Running: rsync "+rsync.format(chmod, sshcommand, pem, inDir+inFile, loginid, host, outDir))
    context.run("rsync "+rsync.format(chmod, sshcommand, pem, inDir+inFile, loginid, host, outDir))

@task
def seekFolders(context):
    pass

@task
def getFolders(context):
    pass

@task
def uploadFolders(context):
    pass

@task
def checkFolders(context):
    pass