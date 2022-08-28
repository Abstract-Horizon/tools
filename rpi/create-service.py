#!/usr/bin/env python3

import argparse
import os.path
from os import stat

from pwd import getpwuid

import sys


DEFAULT_SYSTEMD_LOCATION = "/etc/systemd/system"


parser = argparse.ArgumentParser(description='Ensure hardware configured tool.')

parser.add_argument('--verbose', '-v', help='verbose', action='count', default=0)
parser.add_argument('--quiet', '-q', help='no output', action='store_true', default=False)
parser.add_argument("--dry-run", help="dry run - no files would be written", action='store_true', default=False)


parser.add_argument("-u", "--user", help="user to be used to run daemon from systemd service")
parser.add_argument("-g", "--group", help="group to be used to run daemon from systemd service")
parser.add_argument("-d", "--home-dir", help="dir for service to work in")

group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--file", type=str, help='file to be executed')
group.add_argument("-c", "--command", type=str, help='command to be executed')

parser.add_argument("-n", "--name", help="name of the service")

parser.add_argument("-s", "--start-service", help="start service", action='store_true', default=False)


args = parser.parse_args(sys.argv[1:])

verbose_level = 0 if args.quiet else args.verbose + 1
dry_run = args.dry_run
start_service = args.start_service

name_of_service = args.name
command_to_execute = args.command
file_to_execute = args.file

if not file_to_execute and not command_to_execute:
    parser.error("You must supply command to executed with -c/--command or executable file to execute with -f/--file")

home_dir = args.home_dir
if not home_dir:
    if not file_to_execute:
        parser.error("You must supply home dir with -d/--dir if you have not supplied file to execute.")

    home_dir = os.path.split(os.path.abspath(file_to_execute))[0]
else:
    home_dir = os.path.abspath(home_dir)

if file_to_execute:
    if not os.path.exists(file_to_execute):
        parser.error(f"Supplied file does not exist; '{file_to_execute}'")

    if os.path.isdir(file_to_execute):
        parser.error(f"Supplied directory instead of file; '{file_to_execute}'")

    fixed_file_to_execute = os.path.abspath(file_to_execute)
    if os.path.split(fixed_file_to_execute)[0] == os.path.abspath(home_dir):
        fixed_file_to_execute = os.path.split(file_to_execute)[1]
    # else:
    #     print(f"  not same dir '{os.path.split(fixed_file_to_execute)[0]}' != '{os.path.abspath(home_dir)}'")

    if file_to_execute.endswith(".py"):
        command_to_execute = f"python3 {fixed_file_to_execute}"
    elif not os.access(file_to_execute, os.X_OK):
        parser.error(f"Supplied file is not excutable; '{fixed_file_to_execute}'")

        command_to_execute = fixed_file_to_execute

    if not name_of_service:
        name_of_service = os.path.split(file_to_execute)[1]
        if name_of_service.endswith(".py"):
            name_of_service = name_of_service[:-3]

if not name_of_service:
    parser.error("Please supply name of the service using -n/--name switch!")


user = args.user
if not user:
    if file_to_execute:
        user = getpwuid(stat(file_to_execute).st_uid).pw_name
    else:
        user = os.getlogin()


service_file = f"{DEFAULT_SYSTEMD_LOCATION}/{name_of_service}.service"


if verbose_level > 0:
    print(f"Setting up '{service_file}")

if verbose_level > 1:
    print(f"  got executable '{command_to_execute}'")
    print(f"  run as user '{user}'")
    print(f"  in dir '{home_dir}'")


content = f"""[Unit]
Description={name_of_service}
Wants=network-online.target
After=rsyslog.service
After=network-online.target

[Service]
Restart=on-failure
RestartSec=20s
ExecStart={command_to_execute}
ExecStop=/bin/kill -INT $MAINPID
TimeoutStopSec=10s
User={user}
WorkingDirectory={home_dir}
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
"""

try:
    if verbose_level > 1 or dry_run:
        print("")
        if dry_run:
            print("Following would be written to service file:")
        else:
            print("Writing following to service file:")
        print("------------------------------------")
        print(content)
        print("------------------------------------")
    if not dry_run:
        with open(service_file, "w") as f:
            f.write(content)
except Exception:
    parser.error(f"ERROR: Cannot create '{service_file}'. Maybe to run with sudo?")


def execute_command(cmd: str) -> None:
    try:
        return_code = os.system(cmd)
        if return_code != 0:
            parser.error(f"ERROR: cannot run '{cmd}'")
    except Exception:
        parser.error(f"ERROR: cannot run '{cmd}'")


if not dry_run:
    if verbose_level > 0:
        print("  reloading daemon")
    execute_command("sudo systemctl daemon-reload")

    if verbose_level > 0:
        print("  enabling service")
    execute_command(f"sudo systemctl enable {name_of_service}.service")

    if start_service:
        if verbose_level > 0:
            print("  starting service")
        execute_command(f"sudo systemctl start {name_of_service}.service")
