#!/usr/bin/env python
"""Time It Please: Easy command line timer.
"""

import sys
import os.path
from datetime import datetime, timedelta

FILENAME = os.path.expanduser('~/.tip')
FORMAT = '%Y-%m-%d %H:%M'
DAY_HOURS = 8       # Target hours for the day


#
# Commands
#

def on():
    """Timer start"""
    if is_timer_on():
        print('ERROR: Timer is running. Use "tip off" to stop it first.')
        print('If you forgot to stop it earlier, edit "%s" after' % FILENAME)
        return

    if has_previous_day():
        archive()
        print('Archived previous day')

    record('START %s' % now())
    print('Timer started')


def off():
    """Timer stop"""
    if not is_timer_on():
        print('ERROR: Timer is not running. Use "tip on" to start it.')
        print('If you forgot to start it earlier, edit "%s" after' % FILENAME)
        return

    record('STOP %s' % now())
    print('Timer stopped')


def note():
    """Make a note in record file"""
    content = sys.argv[2]
    record('NOTE %s' % content)
    print('Note added')


def info():
    """Show stats"""

    elapsed, notes, status = parse_file()

    print(long_info(elapsed, notes, status))


#
# Internal functions
#

def record(content):
    """Write content to record file"""
    datafile = open(FILENAME, 'at')
    datafile.write('%s\n' % content)
    datafile.close()


def is_timer_on():
    """Is the timer currently running"""
    _, _, status = parse_file()
    return status == 'ON'


def has_previous_day():
    """Does the file start on a previous day?
    We assume you never work past midnight. Go to bed already.
    """

    today = datetime.now()
    start = file_date()
    return start.day != today.day or start.month != today.month


def file_date():
    """Date at which the file timer starts."""

    start = None
    datafile = open(FILENAME, 'rt')
    for line in datafile:
        line = line.strip()

        cmd = line.split(' ')[0]
        if cmd != 'START':
            continue

        param = ' '.join(line.split(' ')[1:])
        start = datetime.strptime(param, FORMAT)
        break

    return start


def archive():
    """Summarise previous day to archive row"""

    elapsed, notes, _ = parse_file()
    archive_date = file_date().strftime('%Y-%m-%d')
    record('ARCHIVE %s %s' % (archive_date, short_info(elapsed, notes)))

    keep_only_archive()


def keep_only_archive():
    """Removes all lines from file which aren't archive lines."""

    keep = []
    read_datafile = open(FILENAME, 'rt')
    for line in read_datafile:
        line = line.strip()
        if line.startswith('ARCHIVE'):
            keep.append(line)
    read_datafile.close()

    write_datafile = open(FILENAME, 'wt')
    write_datafile.write('\n'.join(keep))
    write_datafile.write('\n')
    write_datafile.close()


def parse_file():
    """Parse the file and:
        - calculate elapsed time
        - group the notes
        - decided whether timer is running.
    """

    notes = []
    elapsed = timedelta(0)

    start = None
    stop = None

    datafile = open(FILENAME, 'rt')
    for line in datafile:

        line = line.strip()
        if not line:
            continue

        cmd = line.split(' ')[0]
        param = ' '.join(line.split(' ')[1:])
        if cmd == 'START':
            start = datetime.strptime(param, FORMAT)

        elif cmd == 'NOTE':
            notes.append(param)

        elif cmd == 'STOP':
            stop = datetime.strptime(param, FORMAT)
            if start:
                elapsed += stop - start
                start = None

    status = 'OFF'
    # Catch any START without a matching STOP
    if start:
        status = 'ON'
        elapsed += datetime.now() - start
        start = None

    return elapsed, notes, status


def short_info(elapsed, notes):
    """One line summary"""
    note_str = ', '.join(notes)
    return '%s %s' % (delta_fmt(elapsed), note_str)


def long_info(elapsed, notes, status):
    """Detailed multi-line info"""

    detail = []
    detail.append('Timer is: %s' % status)

    remaining = timedelta(hours=DAY_HOURS) - elapsed
    if remaining > timedelta(0):
        absolute = datetime.now() + remaining

    detail.append('Elapsed:\t%s' % bold(delta_fmt(elapsed)))

    if remaining:
        detail.append('Remaining:\t%s' % delta_fmt(remaining))

        if status == 'ON':
            detail.append('Finish at:\t%s' % absolute.strftime('%H:%M'))

    if notes:
        note_str = ', '.join(notes)
        detail.append('Notes:\t%s' % note_str)

    return '\n'.join(detail)


def now():
    """Date time of right now, formatted as string"""
    return datetime.now().strftime(FORMAT)


def delta_fmt(delta):
    """timedelta formatted as string"""
    secs = delta.total_seconds()

    if secs < 60:
        return '%0.2d secs' % secs

    hours = 0
    if secs > 3600:
        hours = secs / 3600.0
        secs -= int(hours) * 3600

    mins = secs / 60
    secs -= mins * 60

    return '%0.2d:%0.2d' % (hours, mins)


def bold(msg):
    """'msg' wrapped in ANSI escape sequence to make it bold"""
    return '\033[1m%s\033[0m' % msg


def main(argv=None):
    """Main. Start here."""

    if not argv:
        argv = sys.argv

    cmds = {
        'on': on,
        'start': on,

        'off': off,
        'stop': off,

        'note': note,

        'info': info,
        'status': info}

    if len(argv) >= 2 and argv[1] in cmds:
        cmds[argv[1]]()
    else:
        print('tip [on|off|note] [note content]\n')
        info()


if __name__ == '__main__':
    sys.exit(main())
