#!/usr/bin/env python
"""Time It Please: Easy command line timer.
"""

import sys
import os.path
from datetime import datetime, timedelta

FORMAT = '%Y-%m-%d %H:%M'
FILENAME = os.path.expanduser('~/.tip')
DAY_HOURS = 8       # Target hours for the day


class TimeFile(object):
    """A file containing time information"""

    def __init__(self, filename):
        self.filename = filename

        self.status = 'OFF'
        self.file_date = None
        self.elapsed = timedelta(0)
        self.notes = []

        self.parse_file()

    def parse_file(self):
        """Parse the file and:
            - calculate elapsed time: self.elapsed
            - group the notes: self.notes
            - decided whether timer is running: self.status
            - date at which timer first started: self.file_date
        """

        start = None
        stop = None

        datafile = open(self.filename, 'rt')
        for line in datafile:

            line = line.strip()
            if not line:
                continue

            cmd = line.split(' ')[0]
            param = ' '.join(line.split(' ')[1:])
            if cmd == 'START':
                start = datetime.strptime(param, FORMAT)
                if not self.file_date:
                    self.file_date = start

            elif cmd == 'NOTE':
                self.notes.append(param)

            elif cmd == 'STOP':
                stop = datetime.strptime(param, FORMAT)
                if start:
                    self.elapsed += stop - start
                    start = None

        # Catch any START without a matching STOP
        if start:
            self.status = 'ON'
            self.elapsed += datetime.now() - start
            start = None

    def short_info(self):
        """One line summary"""
        note_str = ', '.join(self.notes)
        return '%s %s' % (delta_fmt(self.elapsed), note_str)

    def long_info(self):
        """Detailed multi-line info"""

        detail = []
        detail.append('Timer is: %s' % self.status)

        detail.append('Elapsed:\t%s' % bold(delta_fmt(self.elapsed)))

        remaining = timedelta(hours=DAY_HOURS) - self.elapsed
        if remaining > timedelta(0):
            absolute = datetime.now() + remaining

            detail.append('Remaining:\t%s' % delta_fmt(remaining))

            if self.status == 'ON':
                detail.append('Finish at:\t%s' % absolute.strftime('%H:%M'))

        if self.notes:
            note_str = ', '.join(self.notes)
            detail.append('Notes:\t%s' % note_str)

        return '\n'.join(detail)

    def is_timer_on(self):
        """Is the timer currently running"""
        return self.status == 'ON'

    def has_previous_day(self):
        """Does the file start on a previous day?
        We assume you never work past midnight. Go to bed already.
        """

        today = datetime.now()
        start = self.file_date
        return start.day != today.day or start.month != today.month


class Timer(object):
    """Main object"""

    def __init__(self, filename):
        self.filename = filename
        self.time_file = TimeFile(filename)

    #
    # Commands
    #

    def on(self):
        """Timer start"""
        if self.time_file.is_timer_on():
            print('ERROR: Timer is running. Use "tip off" to stop it first.')
            print('If you forgot to stop it earlier, edit "%s" after' % self.filename)
            return

        if self.time_file.has_previous_day():
            self.archive()
            print('Archived previous day')

        self.record('START %s' % now())
        print('Timer started')

    def off(self):
        """Timer stop"""
        if not self.time_file.is_timer_on():
            print('ERROR: Timer is not running. Use "tip on" to start it.')
            print('If you forgot to start it earlier, edit "%s" after' % self.filename)
            return

        self.record('STOP %s' % now())
        print('Timer stopped')

    def note(self):
        """Make a note in record file"""
        content = sys.argv[2]
        self.record('NOTE %s' % content)
        print('Note added')

    def info(self):
        """Show stats"""
        print(self.time_file.long_info())

    #
    # Internal functions
    #

    def record(self, content):
        """Write content to record file"""
        datafile = open(self.filename, 'at')
        datafile.write('%s\n' % content)
        datafile.close()

    def archive(self):
        """Summarise previous day to archive row"""

        archive_date = self.time_file.file_date.strftime('%Y-%m-%d')
        self.record('ARCHIVE %s %s' % (archive_date,
                                       self.time_file.short_info()))

        self.keep_only_archive()

    def keep_only_archive(self):
        """Removes all lines from file which aren't archive lines."""

        keep = []
        read_datafile = open(self.filename, 'rt')
        for line in read_datafile:
            line = line.strip()
            if line.startswith('ARCHIVE'):
                keep.append(line)
        read_datafile.close()

        write_datafile = open(self.filename, 'wt')
        write_datafile.write('\n'.join(keep))
        write_datafile.write('\n')
        write_datafile.close()


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

    cmds = ['on', 'off', 'note', 'info']

    timer = Timer(FILENAME)
    if len(argv) >= 2 and argv[1] in cmds:
        func = getattr(timer, argv[1])
        func()
    else:
        print('tip [on|off|note] [note content]\n')
        timer.info()


if __name__ == '__main__':
    sys.exit(main())
