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

## CLI Parameters
Since the program is under active development, running arguments might change in future.

| Parameter            | Required? | Description |
| -------------------- | --------- | ----------- |
| `--config`           | YES       | location of config file |
| `--sequencer`        | YES       | miseq or nextseq |
| `--upload-single-run`| NO        | location of single folder to upload |
| `--pem-file`         | NO        | location of pem file |
| `--create-db`        | NO        | initialise sqlite database |
| `--backup-db`        | NO        | backup sqlite database |
| `--dry-run`          | NO        | test run that just prints uptime on remote server |

## Running

Delete database (recommended when testing)
```
rm local.db
```

Initialise database
```
python illumina_uploader.py --config config.ini --sequencer miseq --create-db
```

Scan folders in a directory and upload (default behavior)
```
python illumina_uploader.py --config config.ini --sequencer miseq
```

To upload one specific folder (will not update db)
```
python illumina_uploader.py --config config.ini --sequencer miseq --upload-single-run 200619_M00325_0209_000000000-J6M35
```

Backup database (specify backup folder in config). This will create a backup database file in following format: backup_YYYY-MM-DD-HH-MM-SS.db
```
python illumina_uploader.py --config config.ini --sequencer miseq --backup-db
```

Dry run test
```
python illumina_uploader.py --config config.ini --sequencer miseq --dry-run
```

## Development by Versions
- ~~v0.0.1 - Test rsync command~~
- ~~v0.0.2 - Finalize rsync command~~
- ~~v0.0.3 - Test one folder from main script~~
- ~~v0.0.4 - SQLite DB integration~~
- ~~v0.0.5 - Add error folder name checking + DB Resume upload feature~~
- ~~v0.0.6 - Bugfix folder name checking~~
- ~~v0.0.7~~
    - ~~Multiple folders upload~~
    - ~~backup database~~
- ~~v0.0.8~~
    - ~~watch directory~~
    - ~~Enhanced logging~~
    - ~~Capture Stdout and Stderr properly~~
- ~~v0.0.9~~
    - ~~watch directory bugfix~~
- v0.1   - Generate update file from DB
- v0.2   - Email functionality
- v0.3   - Web UI
- v0.4   - Progress bar in UI using API
- v0.5   - Advanced Data Integrity checks
- v0.4   - Installer
- v1.0   - First Release
 