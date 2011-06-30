#!/usr/bin/env python

""" This script archives all public videos found in a Vimeo account to archive.org
"""

import os
import sys
import urllib
from logbook import debug, info, warn, error
import utils
import settings
import archive
import requests
import json
from videodownloader.providers.vimeo import Vimeo


bucket = settings.archivedotorg_bucket_for_vimeo


def vimeo_video_ids(user):
    debug("Getting videos for user " + user)
    url = 'http://vimeo.com/api/v2/' + user + '/videos.json'
    data = requests.get(url).read()
    items = json.loads(data)
    return [item['id'] for item in items]


def download(video_id, filename):
    v = Vimeo(id=video_id, title=video_id, ext='mp4')

    if os.path.exists(filename):
        info("File %s already exists. Not downloading.")
    else:
        debug("Downloading %s - %s as %s" % (v.id, v.title, filename))
        v.run()


def main():
    os.chdir('/tmp')
    for video_id in vimeo_video_ids(settings.vimeo_username):
        filename = '%s.mp4' % video_id
        if not archive.exists(bucket, filename):
            download(video_id, filename)
            archive.upload(bucket, filename)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()