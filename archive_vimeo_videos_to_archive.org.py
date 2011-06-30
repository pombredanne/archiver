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


def main():
    os.chdir('/tmp')
    for video_id in vimeo_video_ids(settings.vimeo_username):
        v = Vimeo(id=video_id, ext='mp4')
        filename = '%s.mp4' % v.title

        if not archive.exists(bucket, filename):
            if os.path.exists(filename):
                info("File %s already exists. Not downloading.")
            else:
                debug("Downloading " + filename)
                v.run()

            archive.upload(bucket, filename)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()
