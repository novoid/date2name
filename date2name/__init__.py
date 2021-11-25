#!/usr/bin/env python3
# -*- coding: utf-8 -*-
PROG_VERSION = u"Time-stamp: <2021-11-25 15:25:10 vk>"

"""
date2name
~~~~~~~~~

This script adds (or removes) datestamps to (or from) file(s)

:copyright: (c) 2009-2012 by Karl Voit <tools@Karl-Voit.at>
:license: GPL v2 or any later version
:bugreports: <tools@Karl-Voit.at>

"""

import re
import  os
import  time
import  logging
import  sys
from optparse import OptionParser
import platform

# global variables
PROG_VERSION_DATE = PROG_VERSION[13:23]
FORMATSTRIING_SHORT   = "%y%m%d"
FORMATSTRING_COMPACT  = "%Y%m%d"
FORMATSTRING_STANDARD = "%Y-%m-%d"
FORMATSTRING_MONTH    = "%Y-%m"
FORMATSTRING_WITHTIME = "%Y-%m-%dT%H.%M.%S"
REGEX_PATTERNS = {
    'NODATESTAMP': re.compile('^\D'),
    'SHORT': re.compile('^(\d{2})([01]\d)([0123]\d)([- _])'),
    'COMPACT': re.compile('^(\d{4})([01]\d)([0123]\d)([- _])'),
    'STANDARD': re.compile('^(\d{4})-([01]\d)-([0123]\d)([- _])'),
    'MONTH': re.compile('^(\d{4})-([01]\d)(?!-[0123]\d)([- _])'),
    'WITHTIME_AND_SECONDS': re.compile('^(\d{4})-([01]\d)-([0123]\d)([T :_-])([012]\d)([:.-])([012345]\d)([:.-])([012345]\d)([- _.])'),
    'WITHTIME_NO_SECONDS':  re.compile('^(\d{4})-([01]\d)-([0123]\d)([T :_-])([012]\d)([:.-])([012345]\d)([- _.])'),
    'WITHSECONDS': re.compile('^(\d{4})-([01]\d)-([0123]\d)([T :_-])([012]\d)([:.-])([012345]\d)([:.-])([012345]\d)([- _])'),
}
MAX_PATHLENGTH = 255  # os.pathconf('/', 'PC_PATH_MAX') may be longer but os.rename() seems to have hard-coded 256

# cmdline parsing
USAGE = "\n\
         %prog [options] file ...\n\
\n\
Per default, %prog gets the modification time of matching files\n\
and directories and adds a datestamp in standard ISO 8601+ format\n\
YYYY-MM-DD (http://datestamps.org/index.shtml) at the beginning of\n\
the file- or directoryname.\n\
The delimiter between date/time-stamp and rest of the file name\n\
is an underscore character. If there is a space character in the\n\
file name, a space is used as delimiter instead.\n\
If an existing timestamp is found, its style will be converted to the\n\
selected ISO datestamp format but the numbers stays the same.\n\
Executed with an examplefilename \"file\" this results e.g. in\n\
\"2008-12-31_file\".\n\
Note: Other that defined in ISO 8601+ the delimiter between hours,\n\
minutes, and seconds is not a colon but a dot. Colons are causing\n\
several problems on different file systems and are there fore replaced\n\
with the (older) DIN 5008 version with dots.\n\
\n\
Run %prog --help for usage hints"

# pylint: disable-msg=C0103
parser = OptionParser(usage=USAGE)
parser.add_option("-d", "--directories", dest="onlydirectories",
                  action="store_true",
                  help="modify only directory names")
parser.add_option("-f", "--files", dest="onlyfiles",
                  action="store_true",
                  help="modify only file names")
parser.add_option("-C", "--compact", dest="compact",
                  action="store_true",
                  help="use compact datestamp             (YYYYMMDD)")
parser.add_option("-M", "--month", dest="month",
                  action="store_true",
                  help="use datestamp with year and month (YYYY-MM)")
parser.add_option("-S", "--short", dest="short",
                  action="store_true",
                  help="use short datestamp               (YYMMDD)")
parser.add_option("-w", "--withtime", dest="withtime",
                  action="store_true",
                  help="use datestamp including seconds   (YYYY-MM-DDThh.mm.ss)")
parser.add_option("-r", "--remove", dest="remove",
                  action="store_true",
                  help="remove all known datestamps")
parser.add_option("-m", "--mtime", dest="mtime",
                  action="store_true",
                  help="take modification time for datestamp [default]")
parser.add_option("-c", "--ctime", dest="ctime",
                  action="store_true",
                  help="take creation time for datestamp")
parser.add_option("--delimiter", dest="delimiter", metavar='DELIMITER_STRING',
                  help='use this option to override the delimiter character between ' +
                  'date/time-stamp and the rest. It may be a single character like "_" ' +
                  'or some arbitrary string. Please note that anything else but minus, ' +
                  'space, or underscore may result in not recognizing the delimiter ' +
                  'for further operations such as fixing slightly wrong formatted time-stamps.')
parser.add_option("--nocorrections", dest="nocorrections", action="store_true",
                  help="do not convert existing but slightly wrong formatted date/time-stamps to new format")
parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="do not output anything but just errors on console")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")
parser.add_option("-s", "--dryrun", dest="dryrun", action="store_true",
                  help="enable dryrun mode: just simulate what would happen, do not modify files or directories")
parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")
(options, args) = parser.parse_args()


def handle_logging():
    """Log handling and configuration"""

    if options.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif options.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
    else:
        FORMAT = "%(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def get_converted_basename(matched_pattern, item):
    """returns a new filename based on found timestamp information and currently selected datestamp format"""

    if matched_pattern == "compact":
        logging.debug("item \"%s\" matches compact pattern, doing conversion" % item)
        item_year = item[0:4]
        item_month = item[4:6]
        item_day = item[6:8]
        name_without_datestamp = item[8:]
    elif matched_pattern == "standard":
        logging.debug("item \"%s\" matches standard pattern, doing conversion" % item)
        item_year = item[0:4]
        item_month = item[5:7]
        item_day = item[8:10]
        name_without_datestamp = item[10:]
    elif matched_pattern == "month":
        logging.debug("item \"%s\" matches month pattern, doing conversion" % item)
        item_year = item[0:4]
        item_month = item[5:7]
        logging.info("%s no datestamp information for day, so I will take \"00\" for conversion" % item)
        item_day = "00"
        name_without_datestamp = item[7:]
    elif matched_pattern == "withtime":
        logging.debug("item \"%s\" matches withtime pattern, doing conversion" % item)
        item_year = item[0:4]
        item_month = item[5:7]
        item_day = item[8:10]
        logging.warn("%s ... time will be lost due to conversion" % item)
        if REGEX_PATTERNS['WITHSECONDS'].match(item):
            name_without_datestamp = item[19:]
        else:
            # time-stamp only with hours and minutes:
            name_without_datestamp = item[16:]
    else:
        logging.error("unknown matched pattern (internal error)")

    logging.debug("item \"%s\" got year \"%s\" month \"%s\" day \"%s\"" % (item, item_year, item_month, item_day))

    if options.compact:
        return item_year + item_month + item_day + name_without_datestamp
    elif options.month:
        return item_year + "-" + item_month + name_without_datestamp
    elif options.withtime:
        # FIXXME: probably implement some kind of conversion to withtime-format
        logging.warn("%s: Sorry! Conversion to withtime-format not implemented yet, taking standard format" % item)
        return item_year + "-" + item_month + "-" + item_day + name_without_datestamp
    else:
        return item_year + "-" + item_month + "-" + item_day + name_without_datestamp


def get_timestamp_from_file(formatstring, item):
    """read out ctime or mtime of file and return new itemname"""

    if " " in item:
        delimiter_char = " "
    else:
        delimiter_char = "_"

    if options.delimiter:
        delimiter_char = options.delimiter

    if options.ctime and platform.system() == 'Darwin':
        # see https://github.com/novoid/date2name/issues/6 for macOS-issue with ctime
        return time.strftime(formatstring, time.localtime(os.stat(item).st_birthtime)) + delimiter_char + item
    elif options.ctime and platform.system() != 'Darwin':
        return time.strftime(formatstring, time.localtime(os.path.getctime(item))) + delimiter_char + item
    elif options.mtime:
        return time.strftime(formatstring, time.localtime(os.path.getmtime(item))) + delimiter_char + item
    else:
        logging.error("internal error: not ctime nor mtime chosen! You can correct this by giving a parameter")


def generate_new_basename(formatstring, basename):
    """generates the new itemname; considering options.nocorrections"""

    withtime_and_seconds_components = REGEX_PATTERNS['WITHTIME_AND_SECONDS'].match(basename)
    withtime_no_seconds_components = REGEX_PATTERNS['WITHTIME_NO_SECONDS'].match(basename)

    if options.nocorrections or REGEX_PATTERNS['NODATESTAMP'].match(basename):
        logging.debug("basename \"" + basename + "\" matches nodatestamp-pattern or option nocorrections " +
                      "is set: skipping further pattern matching")
        new_basename = get_timestamp_from_file(formatstring, basename)

    elif withtime_and_seconds_components:
        logging.debug("basename \"%s\" matches withtime-and-seconds pattern" % basename)
        if options.withtime:
            if not (withtime_and_seconds_components.group(1) == 'T' and withtime_and_seconds_components.group(3) == '.' and withtime_and_seconds_components.group(5) == '.'):
                logging.debug("old time pattern does not match the ISO pattern for the delimiter characters. I will modify them.")
                return basename[0:10] + 'T' + basename[11:13] + '.' + basename[14:16] + '.' + basename[17:]
            else:
                logging.debug("old pattern is the same as the recognised, basename stays the same")
                return basename
        else:
            new_basename = get_converted_basename("withtime", basename)

    elif withtime_no_seconds_components:
        logging.debug("basename \"%s\" matches withtime-no-seconds pattern" % basename)
        if options.withtime:
            if not (withtime_no_seconds_components.group(1) == 'T' and withtime_and_seconds_components.group(3) == '.'):
                logging.debug("old time pattern does not match the ISO pattern for the delimiter characters. I will modify them.")
                return basename[0:10] + 'T' + basename[11:13] + '.' + basename[14:]
            else:
                logging.debug("old pattern is the same as the recognised, basename stays the same")
                return basename
        else:
            new_basename = get_converted_basename("withtime", basename)

    elif REGEX_PATTERNS['STANDARD'].match(basename):
        logging.debug("basename \"%s\" matches standard-pattern" % basename)
        if not options.withtime and not options.compact and not options.month:
            logging.debug("old pattern is the same as the recognised, basename stays the same")
            return basename
        else:
            new_basename = get_converted_basename("standard", basename)

    elif REGEX_PATTERNS['COMPACT'].match(basename):
        logging.debug("basename \"%s\" matches compact-pattern" % basename)
        if options.compact:
            logging.debug("old pattern is the same as the recognised, basename stays the same")
            return basename
        else:
            new_basename = get_converted_basename("compact", basename)

    elif REGEX_PATTERNS['SHORT'].match(basename):
        logging.debug("basename \"%s\" matches short-pattern" % basename)
        if options.compact:
            logging.debug("old pattern is the same as the recognised, basename stays the same")
            return basename
        else:
            new_basename = get_converted_basename("compact", basename)

    elif REGEX_PATTERNS['MONTH'].match(basename):
        logging.debug("basename \"%s\" matches month-pattern" % basename)
        if options.month:
            logging.debug("old pattern is the same as the recognised, basename stays the same")
            return basename
        else:
            new_basename = get_converted_basename("month", basename)

    else:
        logging.debug("basename \"%s\" does not match any known datestamp-pattern" % basename)
        new_basename = get_timestamp_from_file(formatstring, basename)

    logging.debug("new basename is \"%s\"" % new_basename)

    return new_basename


def get_full_name(path, filename):
    return path + "/" + filename


def remove_timestamp_from_basename(basename, list_of_regular_expressions=None):
    """Identify timestamp by a given list of regular expressions. Then remove the timestamp from basename."""
    if not list_of_regular_expressions or not isinstance(list_of_regular_expressions, list):
        list_of_regular_expressions = [REGEX_PATTERNS[_] for _ in REGEX_PATTERNS]

    for regular_expression in list_of_regular_expressions:
        if regular_expression.match(basename):
            basename = regular_expression.sub(repl='', string=basename, count=1).strip()

    return basename


def handle_item(path, basename, formatstring):
    """Handle timestamp adding or removing with directories or files"""

    if options.remove:
        logging.debug("removing timestamp from base \"%s\"" % basename)
        new_basename = remove_timestamp_from_basename(basename)
    else:
        logging.debug("••••••••••••••••········· adding timestamp to base \"%s\"" % basename)

        if options.onlyfiles and os.path.isdir(basename):
            logging.debug("skipping directory \"%s\" because of command line option \"-f\"" % basename)
            return

        if options.onlydirectories and os.path.isfile(basename):
            logging.debug("skipping file \"%s\" because of command line option \"-d\"" % basename)
            return

        new_basename = generate_new_basename(formatstring, basename)

    logging.debug("new itemname for \"%s\" will be \"%s\"" % (basename, new_basename))

    if options.dryrun:
        if basename == new_basename:
            logging.info("%s … no modification" % basename)
        else:
            logging.info("%-40s  →  %s" % (get_full_name(path, basename), new_basename))
    else:
        if basename == new_basename:
            logging.info("\"%s\" … no modification" % get_full_name(path, basename))
        else:
            logging.debug("\"%s\" → \"%s\"" % (get_full_name(path, basename), new_basename))
            logging.info("%-40s  →  %s" % (get_full_name(path, basename), new_basename))
            if len(new_basename) > MAX_PATHLENGTH:
                logging.error("ERROR: the current file needs to be renamed with a file name length of " +
                              "%i which is greater than %i. " % (len(new_basename), MAX_PATHLENGTH) +
                              "This usually causes \"[Errno 36] File name too long\" and therefore " +
                              "I ignore this file for now. Please shorten file name for at " +
                              "least %i characters and try again." % (len(new_basename)-MAX_PATHLENGTH))
                sys.exit(1)
            else:
                os.rename(basename, new_basename)


def main():
    """Main function [make pylint happy :)]"""

    if options.version:
        print(os.path.basename(sys.argv[0]) + " " + PROG_VERSION_DATE)
        sys.exit(0)

    if len(args) < 1:
        parser.error("invalid usage")

    if (options.verbose and options.quiet):
        parser.error("please use either verbose (--verbose) or quiet (-q) option")

    if (options.onlyfiles and options.onlydirectories):
        parser.error("please use either option files (-f) or option directories (-f) or none of them (for renaming directories and files)")

    if (options.ctime and options.mtime):
        parser.error("please use either ctime (-c) or mtime (-m) option")

    if (not options.ctime and not options.mtime):
        options.mtime = True

    if (options.compact and options.withtime) \
       or (options.compact and options.month) \
       or (options.month and options.withtime):
        parser.error("please use either the default, short, month, or withtime format")

    # log handling
    handle_logging()

    filelist = args[0:]
    logging.debug("filelist: [%s]" % filelist)

    if options.compact:
        formatstring = FORMATSTRING_COMPACT
    elif options.short:
        formatstring = FORMATSTRIING_SHORT
    elif options.month:
        formatstring = FORMATSTRING_MONTH
    elif options.withtime:
        formatstring = FORMATSTRING_WITHTIME
    else:
        logging.debug("no option given for format string; taking standard format")
        formatstring = FORMATSTRING_STANDARD

    original_path = os.getcwd()

    for item in filelist:
        if os.path.isdir(item) or os.path.isfile(item):
            logging.debug("handling item: " + item + "  <-----------------")

            path = os.path.dirname(item)
            logging.debug("has directory: " + path)
            basename = os.path.basename(item)
            logging.debug("has basename:  " + basename)

            if path:
                os.chdir(path)
            logging.debug("changed cwd to: " + os.getcwd())
            handle_item(os.path.dirname(item), os.path.basename(item), formatstring)
            os.chdir(original_path)

        else:
            logging.critical("%s: is no file or directory (broken link?)" % item)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")

# END OF FILE #################################################################
# vim:foldmethod=indent expandtab ai ft=python tw=120 fileencoding=utf-8 shiftwidth=4
