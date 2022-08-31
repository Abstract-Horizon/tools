#!/usr/bin/env python3

import argparse
import os.path
from typing import List, Optional

import sys

SUBJECT = "subject="
ISSUER = "issuer="

description = """
Ensure the correct order of certificates in a PEM chain.
This script requires the chain to include bag attributes (added if given PEM was created from
a PKCS#12/pfx file) to determine the certificate order.
"""

parser = argparse.ArgumentParser(description=description)

parser.add_argument('--verbose', '-v', help='verbose', action='count', default=0)
parser.add_argument('--quiet', '-q', help='no output', action='store_true', default=False)
parser.add_argument("--dry-run", help="dry run - no files would be written", action='store_true', default=False)
parser.add_argument("-i", "--in", type=str, dest="in_filename", help="input file")
parser.add_argument("-o", "--out", type=str, dest="out_filename", help="output file")

args = parser.parse_args(sys.argv[1:])

verbose_level = 0 if args.quiet else args.verbose + 1
dry_run = args.dry_run

in_filename = args.in_filename
out_filename = args.out_filename


if not in_filename:
    parser.error("ERROR: missing -i/-in filename")

if not os.path.exists(in_filename):
    parser.error(f"Cannot find file {in_filename}")


class Cert:
    def __init__(self):
        self.preamble: List[str] = []
        self.content: List[str] = []
        self.subject = ""
        self.issuer = ""

    def process_preamble(self) -> None:
        for l in self.preamble:
            if l.startswith(SUBJECT):
                self.subject = l[len(SUBJECT):]
            elif l.startswith(ISSUER):
                self.issuer = l[len(ISSUER):]


try:
    if verbose_level > 0:
        print(f"Reading from {in_filename}")
    with open(in_filename, "r") as f:
        file_content = [l[:-1] for l in f.readlines()]
except Exception:
    parser.error(f"Cannot read file {in_filename}")

certs: List[Cert] = []

next_cert = Cert()

if verbose_level > 1:
    print("  parsing content")

preamble = True
for l in file_content:
    if l == "-----BEGIN CERTIFICATE-----":
        next_cert.content.append(l)
        preamble = False
    elif l == "-----END CERTIFICATE-----":
        next_cert.content.append(l)
        certs.append(next_cert)
        next_cert.process_preamble()
        if verbose_level > 1:
            print(f"  ++ parsed content of certificate '{next_cert.subject}'")
        next_cert = Cert()
        preamble = True
    elif preamble:
        next_cert.preamble.append(l)
    else:
        next_cert.content.append(l)


def find_issuer(issuer: str) -> Optional[int]:
    for i, cert in enumerate(certs):
        if cert.subject == issuer:
            return i

    return None


if verbose_level > 1:
    print("  arranging certificates")

i = 0
while i < len(certs):
    cert = certs[i]
    if cert.issuer:
        issuer_index = find_issuer(cert.issuer)
        if issuer_index is not None and issuer_index < i:
            issuer_cert = certs[issuer_index]
            del certs[issuer_index]
            certs.insert(i, issuer_cert)
            if verbose_level > 1:
                print(f"  moved certificate '{issuer_cert.subject}' after '{cert.subject}'")
            if verbose_level > 2:
                print(f"    issuer cert index {issuer_index} was before {i}")
        else:
            i += 1
    else:
        i += 1

if verbose_level > 1:
    print("  preparing result content")

result_content = []
for cert in certs:
    for l in cert.preamble:
        result_content.append(l)
    for l in cert.content:
        result_content.append(l)


if dry_run or verbose_level > 2:
    print("")
    print("Resulting file content:")
    print("------------------------------------------")
    for l in result_content:
        print(l)
    print("------------------------------------------")


if not dry_run:
    if out_filename:
        try:
            if verbose_level > 0:
                print(f"Writing result file {out_filename}")
            with open(out_filename, "w") as f:
                f.writelines([l + "\n" for l in result_content])
        except Exception:
            parser.error(f"Error writing to file {out_filename}")
    else:
        for l in result_content:
            print(l)
