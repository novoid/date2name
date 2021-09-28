#!/bin/usr/env python3

# name:    test_date2name.py
# author:  nbehrnd@yahoo.com
# license: GPL v3, 2021.
# date:    2021-08-30 (YYYY-MM-DD)
# edit:    2021-09-28 (YYYY-MM-DD)
#
"""Test pad for functions by date2name with pytest.

Written for Python 3.9.2 and pytest 6.2.4 for Python 3 as provided by
Linux Debian 12/bookworm, branch testing, this is a programmatic check
of functions offered by date2name.  Deposit this script in the root of
the folder fetched and unzipped from PyPi or GitHub.  If your system
includes both legacy Python 2 and Python 3, pytest for Python 3 likely
is named pytest-3; otherwise only pytest.  Thus, adjust your input on
the CLI accordingly when running either one of

pytest -xv test_date2name.py
pytest-3 -xv test_date2name.py

The script either stops when one of the tests fail, or after completion
of the test sequence.  In both cases, the progress of the ongoing tests
is reported to the CLI."""
import os
import time

from datetime import datetime
from subprocess import getstatusoutput, getoutput

import pytest

PROGRAM = str("./date2name/__init__.py")
TFILE = str("test_file.txt")  # the intermediate test file written

def prepare_testfile():
    """The creation of the test file."""
    with open (TFILE, mode="w") as newfile:
        newfile.write("This is the test file for test_date2name.py.")
    # adjust modification time stamp, based on
    # https://stackoverflow.com/questions/53111614/how-to-modify-the-file-modification-date-with-python-on-mac
    result = os.stat(TFILE)
    os.utime(TFILE, (result.st_atime, result.st_mtime + 10.0))


def query_creation_time(name=TFILE):
    """Determine the time of creation of the file/folder."""
    created = os.stat(name).st_ctime
    created = str(datetime.fromtimestamp(created))
    return created


def query_modification_time(name=TFILE):
    """Determine the time when the file/folder was modified."""
    modified = os.stat(name).st_mtime
    modified = str(datetime.fromtimestamp(modified))
    return modified

def test_create_remove_testfile():
    """Merely check if the test file may be written and removed."""
    prepare_testfile()
    os.remove(TFILE)


def test_script_existence():
    """Merely check for the script's presence."""
    assert os.path.isfile(PROGRAM)


def test_script_version():
    """Check for the correct output of the version.

    CLI equivalence: date2name --version """
    out = getoutput(f"python3 {PROGRAM} --version")
    assert out.strip() == "__init__.py 2018-05-09"

@pytest.mark.parametrize("arg1", [" ", "-f", "--files",
                                  "-m", "--mtime",
                                  "-c", "--ctime"])
def test_default_pattern_YYYY_MM_DD(arg1):
    """Prepend 'YYYY-MM-DD_' to the file name."""
    prepare_testfile()
    day = str("")
    new = str("")

    if arg1 in [" ", "-f", "--files", "-m", "--mtime"]:
        day = query_modification_time().split()[0]

    elif arg1 in ["-c", "--ctime"]:
        day = query_creation_time().split()[0]

    new = "_".join([day, TFILE])
    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg1}")
    assert os.path.isfile(new)
    os.remove(new)

@pytest.mark.parametrize("arg1", ["-C", "--compact",
                                  "-C -f", "--compact -f",
                                  "-C --files", "--compact --files",
                                  "-C -m", "--compact -m",
                                  "-C --mtime", "--compact --mtime",
                                  "-C -c", "--compact -c",
                                  "-C --ctime", "--compact --ctime"])
def test_compact_pattern_YYYYMMDD(arg1):
    """Prepend 'YYYYMMDD_' to the file name."""
    prepare_testfile()
    day = str("")
    new = str("")

    if arg1 in ["-C", "--compact",
                "-C -f", "--compact -f",
                "-C --files", "--compact --files",
                "-C -m", "--compact -m",
                "-C --mtime", "--compact --mtime"]:
        day = query_modification_time().split()[0]

    elif arg1 in ["-C -c", "--compact -c",
                  "-C --ctime", "--compact --ctime"]:
        day = query_creation_time().split()[0]

    # drop the hyphens in the datestamp:
    day = day.replace("-", "")

    new = "_".join([day, TFILE])
    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg1}")
    assert os.path.isfile(new)
    os.remove(new)

@pytest.mark.parametrize("arg1", ["-M", "--month",
                                  "-M -f", "--month -f",
                                  "-M --files", "--month --files",
                                  "-M -m", "--month -m",
                                  "-M --mtime", "--month --mtime",
                                  "-M -c", "--month -c",
                                  "-M --ctime", "--month --ctime"])
def test_compact_month_YYYY_MM(arg1):
    """Prepend 'YYYY-MM_' to the file name."""
    prepare_testfile()
    day = str("")
    new = str("")

    if arg1 in ["-M", "--month",
                "-M -f", "--month -f",
                "-M --files", "--month --files",
                "-M -m", "--month -m",
                "-M --mtime", "--month --mtime"]:
        day = query_modification_time().split()[0]

    elif arg1 in ["-M -c", "--month -c",
                  "-M --ctime", "--month --ctime"]:
        day = query_creation_time().split()[0]

    # trim off the last three characters in the datestamp:
    day = day[:-3]

    new = "_".join([day, TFILE])
    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg1}")
    assert os.path.isfile(new)
    os.remove(new)

@pytest.mark.parametrize("arg1", ["-w -f", "-w --files",
                                  "--withtime -f", "--withtime --files",
                                  "-w -m", "-w --mtime",
                                  "--withtime -m", "--withtime --mtime",
                                  "-w -c", "-w --ctime",
                                  "--withtime -c", "--withtime --ctime"])
def test_default_pattern_YYYY_MM_DDThh_mm_ss(arg1):
    """Prepend 'YYYY-MM-DDThh.mm.ss_' to the file name."""
    prepare_testfile()
    day = str("")
    new = str("")

    if arg1 in ["-w -f", "-w --files",
                "--withtime -f", "--withtime --files",
                "-w -m", "-w --mtime",
                "--withtime -m", "--withtime --mtime"]:
        day = query_modification_time().split()[0]
        second = query_modification_time().split()[1]

    elif arg1 in ["-w -c", "-w --ctime",
                  "--withtime -c", "--withtime --ctime"]:
        day = query_creation_time().split()[0]
        second = query_creation_time().split()[1]

    second = second.split(".")[0]  # use integer seconds only
    second = second.replace(":", ".")  # adjust representation

    new = "".join([day, "T", second, "_", TFILE])

    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg1}")
    assert os.path.isfile(new)
    os.remove(new)

@pytest.mark.parametrize("arg1", ["-S", "--short",
                                  "-S -f", "--short -f",
                                  "-S --files", "--short --files",
                                  "-S -m", "--short -m",
                                  "-S --mtime", "--short --mtime",
                                  "-S -c", "--short -c",
                                  "-S --ctime", "--short --ctime"])
def test_short_pattern_YYMMDD(arg1):
    """Prepend 'YYMMDD_' to the file name."""
    prepare_testfile()
    day = str("")
    new = str("")

    if arg1 in ["-S", "--short",
                "-S -f", "--short -f",
                "-S --files", "--short --files",
                "-S -m", "--short -m",
                "-S --mtime", "--short --mtime"]:
        day = query_modification_time().split()[0]

    elif arg1 in ["-S -c", "--short -c",
                  "-S --ctime", "--short --ctime"]:
        day = query_creation_time().split()[0]

    # drop the hyphens in the datestamp:
    day = day.replace("-", "")
    # drop the first two characters about the year (e.g., 1789 -> 89)
    day = day[2:]

    new = "_".join([day, TFILE])
    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg1}")
    assert os.path.isfile(new)
    os.remove(new)

@pytest.mark.parametrize("arg1", ["default", "short", "compact",
                                  "month", "withtime"])
@pytest.mark.parametrize("arg2", ["-r", "--remove"])
def test_remove_stamp(arg1, arg2):
    """Check the retraction of the leading time stamp."""
    substitution = {"default" : "2021-09-21",
                    "short"   : "210921",
                    "compact" : "20210921",
                    "month"   : "2021-09",
                    "withtime": "2021-09-21T13.59.59"}
    prepend = substitution.get(arg1)

    BASIS = "test.txt"
    TFILE = ""
    TFILE = "_".join([prepend, BASIS])
    with open(TFILE, mode = "w") as newfile:
        newfile.write("This is a test file.")

    test = getoutput(f"python3 {PROGRAM} {TFILE} {arg2}")

    assert os.path.isfile(TFILE) is False  # absence of stamped file
    assert os.path.isfile(BASIS)           # presence unstamped file

    os.remove("test.txt")  # succesful space cleaning for next test
    assert os.path.isfile("test.txt") is False
