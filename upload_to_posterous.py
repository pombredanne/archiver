#! /usr/bin/env python

''' This script posts a video to Posterous site
'''

import os
import sys
from datetime import datetime
from subprocess import call
from logbook import debug, info, warn, error, critical
#import pyposterous
from configobj import ConfigObj
import settings
from utils import start_logging, headify


config = ConfigObj(settings.posterous_config, write_empty_values=True)

def get_url():
    for url in config:
        if not config[url]:
            yield url


def download_url(url):
    debug("Downloading " + url)

    file_name = url.split('/')[-1]

    if os.path.exists(file_name):
        warn(file_name + " already exists. Not downloading")
        return file_name

    cmd = ['wget']
    cmd.append(url)

    call(cmd)

    if not os.path.exists(file_name):
        critical("Could not download " + file_name)
        sys.exit(1)

    debug("Finished Downloading " + file_name)
    return file_name


def upload(file_name):
    debug("Uploading " + file_name)

    this_dir = os.path.basename(os.getcwd())

    title = headify(this_dir) + ' - ' + headify(file_name)
    tags = ", ".join([settings.creator, 'Videos', headify(this_dir)])

    debug("Tile = " + title)
    debug("Tags = " + tags)

    #api = pyposterous.API(username=settings.posterous_username,
                          #password=settings.posterous_password)

    #post = api.new_post(site_id=settings.posterous_siteid,
                        #title=title,
                        #body=title,
                        #tags=tags,
                        #media=open(file_name),
                        #autopost=True)
    #post_id = post.id
    post_id = "20"
    info("Posted to Posterous. Id = " + post_id)
    return post_id


def update(url, post_id):
    now = str(datetime.now())
    debug("Updating config")
    debug(url + " = " + post_id + ", " + now)

    config[url] = [post_id, now]
    config.write()


def main():
    debug('=' * 60)
    for url in get_url():
        file_name = download_url(url)
        post_id = upload(file_name)
        update(url, post_id)


if __name__ == "__main__":
    start_logging(__file__)
    main()
