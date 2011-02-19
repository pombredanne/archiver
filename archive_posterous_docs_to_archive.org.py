#!/usr/bin/env python

""" This script archives all documents (.pdf) found in a posterous site to archive.org
"""

from fnmatch import fnmatch
from logbook import debug, info, warn, error
from BeautifulSoup import BeautifulSoup, SoupStrainer
import pyposterous
import utils
import settings
import archive

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


def main():
    for doc in posterous_docs(settings.posterous_primary_sitename):
        bucket = settings.archivedotorg_pdf_bucket

        if not archive.exists(bucket, utils.get_slugified_filename(doc)):
            item = utils.download(doc)
            archive.upload(bucket, item)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()
