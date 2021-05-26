# illumina-uploader
Lightweight program for Illumina sequencer that watches for new sequence folders and uploads to remote server.

## Features
- Lightweight alternative to [SeqUDAS Client](https://github.com/duanjunhyq/sequdas_client) 
- Keeps track of folders uploaded
- Minimal Dependencies
- Cross platform compatible

## Installing
1. Download latest release zip from https://github.com/BCCDC-PHL/illumina-uploader/releases
2. Unzip the contents into a directory
3. Copy correct config.ini file into directory
4. Open cygwin (https://www.cygwin.com/) in Admin mode and cd into the unzipped directory
5. Create virtual env
```
python -m venv venv
```
6. Activate virtual python environment
```
source ./venv/bin/activate
```
7. Install dependencies
```
pip install -r requirements.txt
```
8. Initialize the database
```
python illumina_uploader.py --create-db
```

## Running

### Typical Run Command
```
python illumina_uploader.py
```

To exit, use "Ctrl + C" keyboard combo. Its safe!

## Advanced Commands

Backup database (recommended once a week)
```
python illumina_uploader.py --backup-db
```

Delete database (useful for testing.. backup db first!)
```
rm local.db
```

To upload one specific folder (will not update db, rather add to ignore list)
```
python illumina_uploader.py --upload-single-run 200619_M00325_0209_000000000-J6M35
```

Specify custom config and sequencer
```
python illumina_uploader.py --config config.ini --sequencer miseq
```

Dry run test (does not upload anything or alters the db, useful for debugging)
```
python illumina_uploader.py --dry-run
```

NextSeq specific, after a reboot:
```
1. Reboot the system
2. login as the 'illumina-data-manager' user
2. Mount the NAS:
  - Open the 'Terminal' application
  - cd illumina-uploader
  - ./mountNextSeqs.sh
  - When prompted for 'illumina-data-manager' enter password to run an admin process and press enter.
  - When prompted for the 'nextseq-mac' enter password to mount a directory and press enter.
    (You will be prompted for the 'nextseq-mac' password three times, once for each of the three NextSeq directories)
3. Activate the virtual environment for the illumina uploader:
  - source ./venv/bin/activate
4. Start the illumina uploader:
  - python illumina_uploader.py
5. Many lines of text will scroll up the screen, showing which directories the uploader is checking for. There will be a message at the bottom saying that it will wait for 5 minutes before checking again. Leave the terminal window open and leave the illumina uploader running.
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
- ~~v0.5~~
    - ~~fix FileNotFoundError~~
    - ~~Fix socket error~~
    - ~~new firstrun.sh script NOT WORKING CORRECTLY~~
    - ~~Fix upload_complete.json: use scp instead of rsync~~
    - ~~Add upload_complete.json: input_directory, output_directory~~
- v0.6
    - Fix upload_complete.json: timestamp_start, input_directory, output_directory and format
    - Fix dry run
    - Add pytests
    - Fix single uploads
- v0.7
    - rerwite db class to use run class for folder tracking
    - quick create ignore.txt file from a given input folder
    - Web UI using flask/django
- v0.8   - Installer and one script run
- v0.9   - Progress bar in UI using API
- v1.0   - Long Term Release (LTM), New feature freeze, only bugfixes

## Troubleshooting
### Problem: `$'\r': command not found`
Solution: Add at the end of `~/.bash_profile` (in /home/USER):
```
export SHELLOPTS
set -o igncr
```

### Problem: `Error: dup() in/out/err failed`
Solution: Install ssh/rsync from cygwin installer. Don't use system ones.

### Problem: How to run SQL statements in SQLITE EXPLORER in VSCode?
Solution: Ctrl + Shift + Q