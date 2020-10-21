#!/usr/bin/env python
from fabric import task

@task
def checkupSystemUptime(context):
    context.run("uptime")

@task
def rsyncFolder(context, args):
    print("Running: rsync "+args["rsync"].format(args["chmod"], args["sshcommand"], args["pem"], args["inDir"]+args["inFile"], args["login"], args["host"], args["outDir"]))
    context.run(   "rsync "+args["rsync"].format(args["chmod"], args["sshcommand"], args["pem"], args["inDir"]+args["inFile"], args["login"], args["host"], args["outDir"]))

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