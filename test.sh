#DO NOT USE UNLESS YOU ARE DEVELOPING THIS APPLICATION
#This script is for rapid testing purposes only, it clears out db and runs in debug mode
rm local.db
illumina-uploader --create-db
illumina-uploader --debug
