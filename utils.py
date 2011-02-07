import os
import sys
from logbook import FileHandler


def remove_extn(string):
    return os.path.splitext(string)[0]

def slugify(string):
    import re
    string = string.strip().lower()
    return re.sub(r'[\s_-]+', '-', string)


def headify(string):
    import re
    string = remove_extn(string)
    return re.sub(r'[\s\W_-]+', ' ', string).title()


def start_logging(filename):
    this_file = os.path.basename(filename)
    log_file = '/var/log/' + remove_extn(this_file) + '.log'

    log_handler = FileHandler(log_file, bubble=True)
    log_handler.push_application()
