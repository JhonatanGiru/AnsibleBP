#! /usr/bin/env python
#-----------------------------------------------------------------------------
# Copyright (c) 2021, Oracle and/or its affiliates. All rights reserved.
# This program is free software: you can modify it and/or redistribute it
# under the terms of:
#
# (i)  the Universal Permissive License v 1.0 or at your option, any
#      later version (http://oss.oracle.com/licenses/upl); and/or
#
# (ii) the Apache License v 2.0. (http://www.apache.org/licenses/LICENSE-2.0)
#-----------------------------------------------------------------------------

"""
A script to help identify memory leaks.

The script argument should be the name of a file containing the trace output
when DPI_DEBUG_LEVEL is set to DPI_DEBUG_LEVEL_MEM (32):

    export DPI_DEBUG_LEVEL=32
    ./myprog >& mem.log
    python mem_leak.py mem.log
"""

import sys

ALLOCATED_STRING = ": allocated "
FREED_STRING = ": freed "

OCI_ALLOCATED_STRING = ": OCI allocated "
OCI_FREED_STRING = ": OCI freed "

def check_memory_use(file_name):
    """
    Checks memory use found in the given file. This file is assumed to have
    been generated by setting DPI_DEBUG_LEVEL to the value 32.
    """
    memory_locations = {}
    ordered_memory_locations = []
    for line in open(file_name):

        # check for ODPI-C allocation
        pos = line.find(ALLOCATED_STRING)
        if pos > 0:
            parts = line[pos + len(ALLOCATED_STRING):].split()
            size = int(parts[0])
            memory_location = parts[3]
            memory_locations[memory_location] = size
            ordered_memory_locations.append(memory_location)
            continue

        # check for ODPI-C free
        pos = line.find(FREED_STRING)
        if pos > 0:
            parts = line[pos + len(FREED_STRING):].split()
            memory_location = parts[2]
            del memory_locations[memory_location]
            ordered_memory_locations.remove(memory_location)
            continue

        # check for OCI allocation
        pos = line.find(OCI_ALLOCATED_STRING)
        if pos > 0:
            parts = line[pos + len(OCI_ALLOCATED_STRING):].split()
            size = int(parts[0])
            memory_location = parts[3]
            memory_locations[memory_location] = size
            ordered_memory_locations.append(memory_location)
            continue

        # check for OCI free
        pos = line.find(OCI_FREED_STRING)
        if pos > 0:
            parts = line[pos + len(OCI_FREED_STRING):].split()
            memory_location = parts[2]
            del memory_locations[memory_location]
            ordered_memory_locations.remove(memory_location)
            continue

    print("Potential Memory Leaks")
    for memory_location in ordered_memory_locations:
        print(memory_location, "-> size",
              memory_locations.get(memory_location))

check_memory_use(sys.argv[1])