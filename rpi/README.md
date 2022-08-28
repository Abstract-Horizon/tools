# Raspberry Pi tools

Set of tools to be used with Raspberry Pi

## Ensure Hardware Configured

Tool to ensure appropriate hardware is set properly in config.txt

At the moment only 'i2c', 'spi', 'i2s' and 'audio' is supported:

```bash
$ ./ensure-hardware.py -h
usage: ensure-hardware.py [-h] [--config-file CONFIG_FILE] [--spi] [--i2c] [--i2s] [--audio] [--verbose] [--quiet]

Ensure hardware configured tool.

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE, -f CONFIG_FILE
  --spi                 Ensures spi is turned on
  --i2c                 Ensures i2c is turned on
  --i2s                 Ensures i2s is turned on
  --audio               Ensures audio is turned on
  --verbose, -v         verbose
  --quiet, -q           no output
```

## Create Service

This is simple helper utility to create systemd service for given executable.

Example usage:
```bash
$ sudo ./create-service.py -v -s -n test-service -f test-service-code.py
 ```

Before running it for real, you can always use --dry-run:

```bash
$ ./create-service.py --dry-run -v -s -n test-service -f test-service-code.py
```


Help:
```bash
$ ./create-service.py -h
usage: create-service.py [-h] [--verbose] [--quiet] [--dry-run] [-u USER] [-g GROUP] [-d HOME_DIR] [-f FILE | -c COMMAND] [-n NAME] [-s]

Ensure hardware configured tool.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         verbose
  --quiet, -q           no output
  --dry-run             dry run - no files would be written
  -u USER, --user USER  user to be used to run daemon from systemd service
  -g GROUP, --group GROUP
                        group to be used to run daemon from systemd service
  -d HOME_DIR, --home-dir HOME_DIR
                        dir for service to work in
  -f FILE, --file FILE  file to be executed
  -c COMMAND, --command COMMAND
                        command to be executed
  -n NAME, --name NAME  name of the service
  -s, --start-service   start service
 ```
