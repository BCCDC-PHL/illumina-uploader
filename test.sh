#rm db
rm local.db
#create new db
python illumina_uploader.py --create-db
#run upload
python illumina_uploader.py --debug