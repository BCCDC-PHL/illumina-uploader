#Script to initialize uploader. Only have to run this the first time ./install.sh
echo "Installing illumina-uploader.."
#Create virtual env
python -m venv venv
#activate virtual env
#source ./venv/bin/activate
./venv/Scripts/activate
#Install dependencies
pip install .
#Initialize the database
illumina-uploader --create-db
echo "..Ready to use!"
source ./venv/Scripts/activate
