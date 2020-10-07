#!/usr/bin/env python

from fabric import task
from configparser import ConfigParser

#logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO)

configObject = ConfigParser()
configObject.read("config.ini")
serverInfo = configObject["SERVER"]
localInfo = configObject["LOCAL"]
commands = configObject["COMMANDS"]
pem = serverInfo["pemfile"]
inDir = localInfo["inputdir"]
host = serverInfo["host"]
loginid = serverInfo["loginid"]
outDir = serverInfo["outputdir"]

@task
def checkupSystemUptime(context):
    context.run("uptime")

@task
def rsyncFolders(context):
    context.run("rsync "+commands["rsynccommand"].format(pem, inDir, loginid, host, outDir))

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