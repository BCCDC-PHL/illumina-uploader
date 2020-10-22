# illumina-uploader
Lightweight program for Illumina sequencer that watches for new sequence folders and uploads to remote server.

## Features
- Lightweight alternative to [SeqUDAS Client](https://github.com/duanjunhyq/sequdas_client) 
- Keeps track of folders uploaded
- Minimal Dependencies
- Cross platform compatible

## Installing
Get all requirements
```
pip install -r requirements.txt
```

## Configuration
The program uses standard python configuration file (.ini format) along with runtime arguments 

### Example config.ini

```
[SERVER]
host = XXX
pemfile = XXX
loginid = XXX
outputdir = /home/jaideep.singh/covid-19_test_rsync/

[LOCAL]
inputdir = /path/to/input/directory/

[COMMANDS]
rsynccommandold = -zahqe "{} -i {}" {} {}@{}:{}
rsynccommand = -artvh -p {} -e "{} -i {}" {} {}@{}:{}
sshnixcommand = ssh
sshwincommand = /usr/bin/ssh
chmodcommand = --chmod=ug=rwx

[DB]
location = local.db
foldertable = folderinfo

[SQL]
createtable = XXX
checkfolderpresence = XXX
insertfolder = XXX
getfolderstoupload = XXX
```

## Running
Initialise database
```
python illumina_uploader.py --config_file config.ini --create_db
```

To upload one specific folder
```
python illumina_uploader.py --config_file config.ini --upload_single_folder 200619_M00325_0209_000000000-J6M34
```

To upload multiple folders
```
TBD
```

To upload all
```
TBD
```

## Development by Versions
- ~~v0.0.1 - Test rsync command~~
- ~~v0.0.2 - Finalize rsync command~~
- ~~v0.0.3 - Test one folder from main script~~
- v0.0.4 - SQLite DB integration
- v0.0.5 - Test multiple folders from main script
- v0.0.6 - Generate update file from DB
- v0.0.7 - MD5 checksums
- v0.0.8 - Enhanced logging
- v0.0.9 - Tests
- v0.1 - Email functionality
- v0.2 - Web UI
- v0.3 - API
 