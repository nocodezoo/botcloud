#!/usr/bin/env python3
"""Sequence number generator for messages"""

import datetime
import sys

SEQ_FILE = "/home/openryanclaw/.openclaw/workspace/.sequence"

def get_next_sequence():
    # Read current sequence
    try:
        with open(SEQ_FILE, "r") as f:
            seq = int(f.read().strip())
    except:
        seq = 0
    
    # Increment
    seq += 1
    if seq > 9999:
        seq = 1
    
    # Save
    with open(SEQ_FILE, "w") as f:
        f.write(f"{seq:04d}")
    
    # Get timestamp
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"[{ts}] #{seq:04d}"

if __name__ == "__main__":
    print(get_next_sequence())
