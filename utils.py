import os
import urllib
import urllib2
import urlparse
from logbook import debug, info, warn, error
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


def exists(url):
    """ Check whether the url exists.
    """
    try:
        urllib2.urlopen(urllib2.Request(url))
        debug(url + " already exists.")
        return True
    except urllib2.HTTPError:
        debug(url + " does not exist")
        return False


def get_filename(url):
    """ Return the last component from url.
    """
    path = urlparse.urlparse(url).path
    last_component = path.split('/')[-1]
    return last_component


def get_slugified_filename(url):
    return slugify(get_filename(url))


def download(url, progress=False):
    """ Download the document pointed to by url to cwd
    """
    filename = get_filename(url)

    if os.path.exists(filename):
        info(filename + " already exists in cwd. Not downloading. ")
    else:
        debug("Downloading " + url)

        if progress:
            import urlgrabber
            from urlgrabber.progress import text_progress_meter

            urlgrabber.urlgrab(url=url,
                               filename=filename,
                               progress_obj=text_progress_meter())
        else:
            urllib.urlretrieve(url=url, filename=filename)

        debug("Finished Downloading " + filename)

    return filename


def start_logging(filename):
    this_file = os.path.basename(filename)
    log_file = '/var/log/' + remove_extn(this_file) + '.log'

    log_handler = FileHandler(log_file, bubble=True)
    log_handler.push_application()
