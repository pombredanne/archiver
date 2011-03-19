#!/usr/bin/env python

""" This script archives all public photos found in a Flickr account to archive.org
"""

import os
import sys
import urllib
from logbook import debug, info, warn, error
import utils
import settings
import flickr
import archive


def process(photoset):
    debug("Processing " + photoset.title)

    bucket = photoset.id
    if archive.exists(bucket):
        return

    debug("Creating archive.org bucket " + bucket)
    archive.create_bucket(bucket,
                          title=photoset.title,
                          description=photoset.description,
                          keywords=photoset.title,
                          mediatype='movies'
                         )

    for photo in photoset.getPhotos():
        url = photo.getLarge()
        item = utils.download(url)
        archive.upload(bucket, item, progress=False)
        os.remove(item)


def main():
    flickr.API_KEY = settings.flickr_api_key
    flickr.API_SECRET = settings.flickr_api_secret
    user = flickr.User(id=settings.flickr_id)

    debug("Getting Photosets for user " + user.id)
    for photoset in user.getPhotosets():
        process(photoset)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()
