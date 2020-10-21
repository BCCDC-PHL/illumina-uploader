# illumina-uploader
Watch for new files in Illumina sequencer and upload to remote server

## Installing
Get all requirements
```
pip install -r requirements.txt
```
## Usage
To rsync folders with 10 second timeout
```
fab -T 10 rsyncFolders
```

List all available commands
```
fab --list
```

Note: Other commands are not available right now.

## Example Config File

### config.ini

```
[SERVER]
host = XXX
pemfile = XXX
loginid = XXX
outputdir = /path/to/covid-19_test_rsync/

[LOCAL]
inputdir = /path/to/inputFiles/200901_M00325_0225_000000000-G66LJ

[COMMANDS]
rsynccommand = -zahqe "ssh -i {}" {} {}@{}:{}
```

## Development by Versions
- v0.0.1 - Finalize rsync command
- v0.0.2 - Calling from outside script
- v0.0.3 - SQLite DB
- v0.0.4 - Email functionality
- v0.0.5 - Web UI
 