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

## Running
Since the program is under active development, running arguments might change in future.

| Parameter          | Required? | Description |
| ------------------ | --------- | ----------- |
| `--config`         | YES       | location of config file |
| `--sequencer`      | YES       | miseq or nextseq |
| `--upload-folder`  | NO        | location of single folder to upload |
| `--scan-directory` | NO        | scan directory specified in config file |
| `--pem-file`       | NO        | location of pem file |
| `--create-db`      | NO        | initialise sqlite database |
| `--backup-db`      | NO        | backup sqlite database |

Delete database before testing, as the schema is not yet finalized.
```
rm local.db
```

Initialise database
```
python illumina_uploader.py --config config.ini --sequencer miseq --create-db
```

To upload one specific folder
```
python illumina_uploader.py --config config.ini --sequencer miseq --upload-folder 200619_M00325_0209_000000000-J6M35
```

Scan folders in a directory
```
python illumina_uploader.py --config config.ini --sequencer miseq --scan-directory
```

Resume uploading folders from database
```
python illumina_uploader.py --config config.ini --sequencer miseq
```

Dry run test (Does not upload anything)
```
TBD
```

Backup database
```
TBD
```

## Development by Versions
- ~~v0.0.1 - Test rsync command~~
- ~~v0.0.2 - Finalize rsync command~~
- ~~v0.0.3 - Test one folder from main script~~
- ~~v0.0.4 - SQLite DB integration~~
- ~~v0.0.5 - Add error folder name checking + DB Resume upload feature~~
- ~~v0.0.6 - Bugfix folder name checking~~
- v0.0.7
    - Test multiple folders using DB
    - backup database
- v0.0.8
    - Enhanced logging
    - Capture Stdout and Stderr
- v0.0.9
    - Dry run argument
    - Generate update file from DB
- v0.1   - MVP release
- v0.2   - Email functionality
- v0.3   - Web UI
- v0.4   - Progress bar in UI using API
- v0.5   - Advanced Data Integrity checks
- v0.4   - Installer
- v1.0   - First Release
 