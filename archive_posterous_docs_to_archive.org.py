#!/usr/bin/env python

""" This script archives all documents (.pdf) found in a posterous site to archive.org
"""

import os
import urllib
import urllib2
import urlparse
from subprocess import call
from fnmatch import fnmatch
from logbook import debug, info, warn, error
import pyposterous
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, SoupStrainer
from utils import start_logging, slugify
import settings

pattern = 'http://posterous.com/*.pdf'


def posterous_docs(sitename, num_posts=50):
    """ Return the list of all documents found in the posterous site
    """
    debug("Getting the list of docs for the posterous site " + sitename)
    docs = []

    for post in pyposterous.api.read_posts(hostname=sitename, num_posts=num_posts):
        links = [link.get('href') for link in BeautifulSoup(post.body, parseOnlyThese=SoupStrainer('a'))]

        for link in links:
            if fnmatch(link, pattern):
                docs.append(link)

    docs = list(set(docs))  # Remove duplicates
    return docs


def get_filename(url):
    """ Return only the last portion from url.
    """
    path = urlparse.urlparse(url).path
    last_component = path.split('/')[-1]
    return slugify(last_component)


def download(url, filename):
    if os.path.exists(filename):
        info(filename + " already exists in the cwd. Not downloading")
    else:
        debug("Downloading " + filename)
        urllib.urlretrieve(url, filename)
        debug("Finished downloading " + filename)


def exists_in_archivedotorg(bucket, item):
    url = settings.archivedotorg_download_base + bucket + "/" + item

    try:
        f = urllib2.urlopen(urllib2.Request(url))
        debug(item + " already exists in archive.org")
        return True
    except urllib2.HTTPError:
        return False


def upload_to_archivedotorg(bucket, item):
    """ Upload the item to bucket in archive.org
    """
    debug('Uploading ' + item + ' to ' + bucket)

    cmd = []

    #cmd.append('echo') # for testing
    cmd.append('curl')
    cmd.append('--location')

    cmd.append('--header')
    cmd.append('authorization : LOW '
               + settings.archivedotorg_access_key
               + ':'
               + settings.archivedotorg_secret_key)

    cmd.append('--progress-bar')
    cmd.append('--output')
    cmd.append(item + '.log')
    cmd.append('--upload-file')
    cmd.append(item)
    cmd.append(settings.archivedotorg_upload_base + bucket + '/')

    call(cmd)

    debug('Finished ' + item)


def main():
    for doc in posterous_docs(settings.posterous_sitename):
        bucket = settings.archivedotorg_pdf_bucket
        filename = get_filename(doc)

        if not exists_in_archivedotorg(bucket, filename):
            download(doc, filename)
            upload_to_archivedotorg(bucket, filename)


if __name__ == "__main__":
    start_logging(__file__)
    main()
