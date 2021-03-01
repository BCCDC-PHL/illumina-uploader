#DO NOT USE UNLESS YOU ARE DEVELOPING THIS APPLICATION
#This script is for rapid testing purposes only, it clears out db and runs in debug mode
#rm db
rm local.db
#create new db
python illumina_uploader.py --create-db
#run upload
python illumina_uploader.py --debug