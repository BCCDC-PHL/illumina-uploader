#!/usr/bin/env python
from fabric import task

@task
def checkupSystemUptime(context):
    context.run("uptime")

@task
def rsyncFolder(context, args):
    print("Running: rsync "+args["rsync"].format_map(args))
    context.run(   "rsync "+args["rsync"].format_map(args))

@task
def scanFolders(context, args):
    pass

