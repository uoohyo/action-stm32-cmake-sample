#!/usr/bin/env python3
"""Verify build outcome and a fresh, nonempty output from this job."""
import argparse
from pathlib import Path
import struct


def verify(outcome, directory, expected, elf=False):
    if outcome != "success":
        raise ValueError("Build action did not succeed")
    files = [p for p in Path(directory).rglob("*")
             if p.is_file() and p.suffix in (".out", ".elf") and p.stat().st_size > 0]
    target = Path(expected)
    if not target.is_file() or target.stat().st_size == 0:
        if len(files) != 1:
            raise ValueError("Expected one nonempty output in the cleaned configuration directory")
        target = files[0]
    if elf:
        data = target.read_bytes()[:20]
        if len(data) < 20 or data[:4] != b"\x7fELF" or data[4:6] != b"\x01\x01" or struct.unpack("<H", data[18:20])[0] != 40:
            raise ValueError("Expected a 32-bit little-endian ARM ELF")
    return target

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outcome")
    parser.add_argument("directory")
    parser.add_argument("expected")
    parser.add_argument("--elf", action="store_true")
    args = parser.parse_args()
    print(verify(args.outcome, args.directory, args.expected, args.elf))
