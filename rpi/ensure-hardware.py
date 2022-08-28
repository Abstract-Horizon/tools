#!/usr/bin/env python3

import argparse
import os.path
from typing import List

import sys

CONFIG_FILE = "/boot/config.txt"

parser = argparse.ArgumentParser(description='Ensure hardware configured tool.')

parser.add_argument("--config-file", "-f", default=CONFIG_FILE)
parser.add_argument("--spi", action='store_true', default=False, help="Ensures spi is turned on")
parser.add_argument("--i2c", action='store_true', default=False, help="Ensures i2c is turned on")
parser.add_argument("--i2s", action='store_true', default=False, help="Ensures i2s is turned on")
parser.add_argument("--audio", action='store_true', default=False, help="Ensures audio is turned on")
parser.add_argument('--verbose', '-v', help='verbose', action='count', default=0)
parser.add_argument('--quiet', '-q', help='no output', action='store_true', default=False)


args = parser.parse_args(sys.argv[1:])

config_file = args.config_file
verbose_level = 0 if args.quiet else args.verbose + 1


def read_config(config_file: str) -> List[str]:
    try:
        with open(config_file, "r") as f:
            return [l[:-1] for l in f.readlines()]
    except Exception:
        parser.error(f"ERROR: Cannot read from '{config_file}'. Maybe to run with sudo?")


def ensure_hardware(config_lines: List[str], interface_str: str, hardware_str: str) -> bool:
    comment_line_no = [i for i, l in enumerate(config_lines) if l.startswith("# Uncomment some or all of these to enable the optional hardware interfaces")]
    i2c_arm_line = [(i, l) for i, l in enumerate(config_lines) if f"dtparam={hardware_str}" in l]
    while len(i2c_arm_line) > 1:
        del config_lines[i2c_arm_line[-1][0]]

    insert_at = -1
    if len(i2c_arm_line) < 0:
        insert_at = len(config_lines) if len(comment_line_no) == 0 else comment_line_no[0]
    else:
        existing_line_no = i2c_arm_line[0][1]
        if existing_line_no != f"dtparam={hardware_str}=on":
            insert_at = i2c_arm_line[0][0]
            if verbose_level > 1:
                print(f"  -- removing existing line '{config_lines[insert_at]}'")
            del config_lines[insert_at]

    if insert_at >= 0:
        new_value = f"dtparam={hardware_str}=on"
        if verbose_level > 0:
            print(f"  ++ adding '{interface_str}'")
        if verbose_level > 1:
            print(f"  -- inserting '{new_value}' at line {insert_at}")
        config_lines.insert(insert_at, new_value)
        return True

    if verbose_level > 1:
        print(f"  Found '{i2c_arm_line[0][1]}' - no changes to file")
    return False


def write_config(config_file: str, config_lines: List[str]) -> None:
    backup_file = config_file[:-3] + "bak" if config_file.endswith(".txt") else config_file + ".bak"
    try:
        if os.path.exists(backup_file):
            if verbose_level > 1:
                print(f"  removing old backup file '{backup_file}'")
            os.remove(backup_file)
    except Exception:
        parser.error(f"ERROR: Cannot remove '{backup_file}'. Maybe to run with sudo?")

    try:
        if verbose_level > 1:
            print(f"  renaming existing file '{config_file}' to backup file '{backup_file}'")
        os.rename(config_file, backup_file)
    except Exception:
        parser.error(f"ERROR: Cannot rename '{config_file}' to '{backup_file}'. Maybe to run with sudo?")

    try:
        with open(config_file, "w") as f:
            f.writelines([l + "\n" for l in config_lines])
    except Exception:
        parser.error(f"ERROR: Cannot write to '{config_file}'. Maybe to run with sudo?")


if verbose_level > 0:
    print(f"Reading {config_file}...")

config_lines = read_config(config_file)

file_changed = False
if args.i2c: file_changed = ensure_hardware(config_lines, "i2c", "i2c_arm") or file_changed
if args.i2s: file_changed = ensure_hardware(config_lines, "i2s", "i2s") or file_changed
if args.spi: file_changed = ensure_hardware(config_lines, "spi", "spi") or file_changed
if args.audio: file_changed = ensure_hardware(config_lines, "audio", "audio") or file_changed


if file_changed:
    if verbose_level > 0:
        print("")
        print(f"Writing back amended {config_file}...")

    write_config(config_file, config_lines)

    if verbose_level > 0:
        print("")
        print("*** Don't forget to restart Raspberry Pi")

else:
    if verbose_level > 0:
        print("No changes needed to the file")
