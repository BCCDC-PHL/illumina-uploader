# illumina-uploader
Lightweight program for Illumina sequencer that watches for new sequence folders and uploads to remote server.

## Features
- Lightweight alternative to [SeqUDAS Client](https://github.com/duanjunhyq/sequdas_client) 
- Keeps track of folders uploaded
- Minimal Dependencies
- Cross platform compatible

## Installing
Download latest release zip from https://github.com/BCCDC-PHL/illumina-uploader/releases

Unzip and Goto directory and activate Python Virtual Environment
```
python -m venv venv
source ./venv/bin/activate
```

Get all required python packages
```
pip install -r requirements.txt
```

## Running

### Normal Commands

First time run (initialize database)
```
python illumina_uploader.py --create-db
```

Normal Run
```
python illumina_uploader.py
```

Backup database (recommended once a week)
```
python illumina_uploader.py --backup-db
```

## Advanced Commands

To upload one specific folder (will not update db, rather add to ignore list)
```
python illumina_uploader.py --upload-single-run 200619_M00325_0209_000000000-J6M35
```

Delete database (useful for testing.. backup db first!)
```
rm local.db
```

Specify custom config and sequencer
```
python illumina_uploader.py --config config.ini --sequencer miseq
```

Dry run test
```
python illumina_uploader.py --dry-run
```

## CLI Parameters
Since the program is under active development, running arguments might change in future.

| Optional Parameter   | Description |
| -------------------- | ----------- |
| `--sequencer`        | miseq or nextseq (Default taken from config file) |
| `--config`           | location of config file |
| `--upload-single-run`| location of single folder to upload |
| `--pem-file`         | location of pem file |
| `--create-db`        | initialise sqlite database |
| `--backup-db`        | backup sqlite database |
| `--dry-run`          | test run that just prints uptime on remote server |

## Config file
The program uses standard python configuration file along with runtime arguments. 
See [config.ini.template](config.ini.template) for format details.

## Version Changes
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
- ~~v0.3~~
     - ~~upload from two locations~~
     - ~~fix mail message timezone~~
- ~~v0.4~~
     - ~~add multiple output locations for nextseqs~~
     - ~~fix ssl problem in email~~
     - ~~fix nextseq regex~~
     - ~~fix before and after email format for lab~~
     - ~~remove COPY_COMPLETE file~~
     - ~~add upload_complete.json with start_upload_time and end_upload_time~~
     - ~~change UPLOADED to FINISHED in db~~
     - ~~fix timezone in log messages~~
     - ~~fix crash when rsync network error~~
     - ~~update config.ini.template~~
- v0.5
    - simplify sending emails
    - rerwite db class to use run class for folder tracking
    - fix dry run
    - Add pytest
    - update upload_complete.json: checksum, input_directory, output_directory
    - quick create ignore.txt file from a given input folder
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