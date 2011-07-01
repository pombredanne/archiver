#!/usr/bin/env python

import os
from datetime import date
from logbook import debug, info, warn, error
import settings
import utils
import boto
import progressbar


collection = {'texts' : 'opensource',
              'audio' : 'opensource_audio',
              'movies' : 'opensource_movies'
             }


conn = boto.connect_ia(settings.archivedotorg_access_key,
                       settings.archivedotorg_secret_key)
pbar = None


def exists(bucket, key=""):
    """ Check whether key exists in bucket in archive.org
    """
    try:
        bucket = conn.get_bucket(bucket)
    except boto.exception.S3ResponseError, e:
        if e.error_code == 'NoSuchBucket':
            return False
        else:
            raise e

    if key:
        return bool(bucket.get_key(key))
    else:
        return True


def create_bucket(bucket,
                  mediatype,
                  title,
                  description='',
                  creator=settings.archivedotorg_creator,
                  date=date.today().strftime("%Y-%m-%d"),
                  keywords=''):
    """ Create the bucket in archive.org
    """
    if exists(bucket):
        info("Bucket " + bucket + " already exists.")
        return

    debug("Creating bucket " + bucket + " in archive.org.")

    headers = {"x-archive-meta-mediatype":mediatype,
               "x-archive-meta-collection":collection[mediatype],
               "x-archive-meta-title":str(title),
               "x-archive-meta-description":str(description),
               "x-archive-meta-creator":str(creator),
               "x-archive-meta-date":str(date),
               "x-archive-meta-subject":str(keywords),
               "x-archive-meta-licenseurl":"http://creativecommons.org/licenses/by-nc/3.0"
              }

    conn.create_bucket(bucket, headers)


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


def progress_callback(current, total):
    try:
        pbar.update(current)
    except AssertionError, e:
        print e


def upload(bucket, filename):
    debug("Uploading " + filename + " to " + bucket)

    if not exists(bucket):
        error("Bucket " + bucket + " does not exist.")
        return

    if exists(bucket, filename):
        info("File " + filename + " in bucket " + bucket + " already exists.")
        return

    bucket = conn.get_bucket(bucket)
    key = bucket.new_key(filename)

    size = os.stat(filename).st_size
    if size == 0:
        error("Bad filesize for '%s'" % (filename))
        return

    widgets = [
        unicode(str(filename), errors='ignore').encode('utf-8'), ' ',
        progressbar.FileTransferSpeed(),
        ' <<<', progressbar.Bar(), '>>> ',
        progressbar.Percentage(), ' ', progressbar.ETA()
    ]
    global pbar
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=size)
    pbar.start()

    try:
        key.set_contents_from_filename(
            filename,
            cb=progress_callback,
            num_cb=100
        )
    except IOError, e:
        print e

    pbar.finish()

