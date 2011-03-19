#!/usr/bin/env python

from subprocess import call
from datetime import date
from logbook import debug, info, warn, error
import settings
import utils

collection = {'texts' : 'opensource',
              'audio' : 'opensource_audio',
              'movies' : 'opensource_movies'
             }


def exists(bucket, item=""):
    """ Check whether item exists in bucket in archive.org
    """
    if item:
        base = settings.archivedotorg_download_base + bucket + "/"
        url =  base + item
        url1 = base + utils.slugify(item)

        return utils.exists(url) or utils.exists(url1)
    else:
        url = settings.archivedotorg_details_base + bucket
        return utils.exists(url)





def create_bucket(bucket,
                  mediatype,
                  title,
                  description='',
                  creator=settings.archivedotorg_creator,
                  date=date.today().strftime("%Y-%m-%d"),
                  keywords=''):
    """ Create the bucket in archive.org
    """
    debug("Creating " + bucket + " in archive.org")
    cmd = []

    def add(key, value):
        cmd.append('--header')
        cmd.append(str(key) + ':' + str(value))

    #cmd.append('echo') # for testing
    cmd.append('curl')
    cmd.append('--location')

    add('x-archive-auto-make-bucket', 1)
    add('x-archive-ignore-preexisting-bucket', 1)
    add('authorization', ' LOW ' + settings.archivedotorg_access_key + ':' + settings.archivedotorg_secret_key)
    add('x-archive-meta-mediatype', mediatype)
    add('x-archive-meta-collection', collection[mediatype])
    add('x-archive-meta-title', title)
    add('x-archive-meta-description', description)
    add('x-archive-meta-creator', creator)
    add('x-archive-meta-date', date)
    add('x-archive-meta-subject', keywords)
    add('x-archive-meta-licenseurl', 'http://creativecommons.org/licenses/by-nc/3.0/')
    cmd.append('--upload-file')
    cmd.append('/dev/null')

    cmd.append(settings.archivedotorg_upload_base + bucket)

    call(cmd)


def upload(bucket, item):
    """ Upload the item to bucket in archive.org
    """
    debug('Uploading ' + item + ' to ' + bucket)

    #if exists(bucket, utils.slugify(item)):
        #warn(item + " already exists in archive.org. Not uploading.")
        #return

    cmd = []

    #cmd.append('echo') # for testing
    cmd.append('curl')
    cmd.append('--location')

    cmd.append('--header')
    cmd.append('authorization: LOW '
               + settings.archivedotorg_access_key
               + ':'
               + settings.archivedotorg_secret_key)

    cmd.append('--verbose')
    cmd.append('--progress-bar')
    cmd.append('--output')
    cmd.append(item + '.log')
    cmd.append('--upload-file')
    cmd.append(item)
    cmd.append(settings.archivedotorg_upload_base + bucket + '/' + utils.slugify(item))

    call(cmd)

    #try:
        #call(cmd)
    #except KeyboardInterrupt:
        # Sometimes curl is hanging even after uploading the item is 100% done.
        # In that case, I have to press ctrl+c to continue with next item.
        #warn("Received Ctrl+c. Returning.")


    debug('Finished ' + item)
