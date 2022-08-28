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
