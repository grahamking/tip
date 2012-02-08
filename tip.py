#!/usr/bin/env python
"""Time It Please: Easy command line timer.
"""

import sys
import os.path
from datetime import datetime, timedelta

FILENAME = os.path.expanduser('~/.tip')
FORMAT = '%Y-%m-%d %H:%M'
DAY_HOURS = 8       # Target hours for the day


def on():
    """Timer start"""
    # TODO: If different date erase file
    record('START %s' % now())


def off():
    """Timer stop"""
    record('STOP %s' % now())


def note():
    """Make a note in record file"""
    content = sys.argv[2]
    record('NOTE %s' % content)


def record(content):
    """Write content to record file"""
    datafile = open(FILENAME, 'at')
    datafile.write('%s\n' % content)
    datafile.close()


def info():
    """Show stats"""

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

    print('Timer is: %s' % status)

    print('Elapsed:\t%s' % bold(delta_fmt(elapsed)))

    for_eight = timedelta(hours=DAY_HOURS) - elapsed
    print('Eight in:\t%s' % delta_fmt(for_eight))

    absolute = datetime.now() + for_eight
    print('Finish at:\t%s' % absolute.strftime('%H:%M'))

    if notes:
        print('Notes:\t%s' % ', '.join(notes))


def now():
    """Date time of right now, formatted as string"""
    return datetime.now().strftime(FORMAT)


def delta_fmt(delta):
    """timedelta formatted as string"""
    secs = delta.total_seconds()
    display = ''

    hours = 0
    if secs > 3600:
        hours = secs / 3600.0
        secs -= int(hours) * 3600
        display += '%d hours ' % hours

    mins = 0
    if secs > 60:
        mins = secs / 60
        secs -= mins * 60
        display += '%0.2d mins ' % mins

    if secs:
        display += '%0.2d secs' % secs

    return display


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
