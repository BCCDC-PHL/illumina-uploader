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
The program uses standard python configuration file along with runtime arguments. 
See [config.ini.template](config.ini.template) for format details.

## CLI Parameters
Since the program is under active development, running arguments might change in future.

| Parameter            | Required? | Description |
| -------------------- | --------- | ----------- |
| `--sequencer`        | NO       | miseq or nextseq (Default taken from config file) |
| `--config`           | NO       | location of config file |
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

## Changelog
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
- ~~v0.0.9 - watch directory bugfix~~
- ~~v0.1~~
     - ~~Generate update.txt and ignore.txt files~~
     - ~~Generate COPY_COMPLETE file for each run directory~~
- ~~v0.2~~
     - ~~output mail folder in remote server~~
     - ~~simplified run script~~
- v0.3   - enhance mail message and fix dry run
- v0.4   - run instrument error files send via email
- v0.5   - JSON status file: file status, checksum, num_files, timestamp
- v0.6   - Web UI using flask/django
- v0.7   - Advanced Data integrity check
- v0.8   - Installer and one script run
- v0.9   - Progress bar in UI using API
- v1.0   - Long Term Release (LTM), New feature freeze, only bugfixes

## Troubleshooting
Problem: `$'\r': command not found`

Solution: Add at the end of `~/.bash_profile` (in /home/USER):
```
export SHELLOPTS
set -o igncr
```

Problem: `Error: dup() in/out/err failed`

Solution: Install ssh/rsync from cygwin installer. Don't use system ones.

Problem: How to run SQL statements in SQLITE EXPLORER in VSCode?

Solution: Ctrl + Shift + Q