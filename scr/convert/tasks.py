import logging
import mimetypes
import tempfile
import urllib2
import os
import json
import subprocess
import shutil
import re

import Image
import slumber
import requests
from django_statsd.clients import statsd
from requests.auth import HTTPDigestAuth
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from celery.task import task
from celery.task import Task
from celery.task.sets import subtask
from celery.exceptions import WorkerLostError
# Setup logging and stats
log = logging.getLogger(__name__)
statsd

# Register the streaming http handlers with urllib2
register_openers()

# Celery tasks
auth = HTTPDigestAuth('bot','93bebc404a38b620b84505644d7ea934e7957331')
api = slumber.API('http://localhost/api/v1',
    auth=auth)

@task(acks_late=True)
def create_pdf(document_pk, type='pdf', callback=None):
    doc = api.document(document_pk).get()
    log.info('Starting conversion of: %s', doc[u'title'])
    for pack in doc[u'packs']:
        if pack[u'type'] == u'pdf':
            log.info('DerivedPack with pdf type. Creation stopped')
            return True

    statsd.incr('attemped_conversions')

    # Get the file using the absolute url
    url = 'http://localhost' + doc[u'download_url']

    req = requests.get(url, auth=auth)
    if req.status_code != 200:
        statsd.incr('failed_conversions')
        log.warn('Did not get a HTTP 200 code when retrieving document.' +
            'Aborting convertion. Error Returned: %s - %s - %s',
            req.url, req.status_code, req.text)

        create_pdf.retry()

    if not 'content-type' in req.headers:
        statsd.incr('failed_conversions')
        log.error('No mime type returned will document request')
        return False

    if req.headers['content-type'] == 'application/pdf':
        log.info("Can't convert pdf's")
        if callback:
            subtask(callback).delay()
        return False

    extension = mimetypes.guess_extension(req.headers['content-type'])

    # Create a temp file using the extension derived from the mime-type
    # 3mb spooled file
    file = tempfile.SpooledTemporaryFile(max_size=3*1000000,suffix=extension)

    for data in req.iter_content(10240):
        file.write(data)

    # Seek to front of file before we stream to the convert service
    file.seek(0)

    # Botched file streaming
    headers = {}
    try:
        filesize = os.fstat(file.fileno()).st_size
    except (OSError, AttributeError):
        try:
            fileobj.seek(0, 2)
            filesize = fileobj.tell()
            fileobj.seek(0)
        except:
            statsd.incr('failed_conversions')
            log.error('Unable to determine original file filesize')
            return False

    headers['Content-Type'] = req.headers['content-type']
    headers['Accept']= "application/pdf"
    headers['Content-Length'] = '%s' % filesize

    def yielder():
        while True:
            block = file.read(10240)
            if block:
                yield block
            else:
                break

    try:
        req = urllib2.Request("http://localhost:8080/converter2/service",
            yielder(), headers)

        # Get the return file
        return_file = urllib2.urlopen(req)
        new_file = tempfile.NamedTemporaryFile(suffix='.pdf')
        while True:
            data = return_file.read(10240)
            if data:
                new_file.write(data)
            else:
                break

    except urllib2.HTTPError as e:
        statsd.incr('failed_conversions')
        msg = e.msg
        if e.fp:
            msg += ' - %s' % e.fp.read()
        log.error('Conversion service error: %s - %s - %s', e.hdrs, e.code, msg)
        create_pdf.retry()

    # Seek file to beginning so we can post it back to the main service
    try:
        new_file.seek(0)

        # Create a new derivedfile pack
        pack = api.derivedpack.post({"type": "pdf", "document": doc["resource_uri"]})

        url = "http://localhost/api/v1/document/%s/pack/%s/derived_file/" % (
            document_pk, pack["id"])

        datagen, headers = multipart_encode({'file': new_file, 'order':'0'})

        request = urllib2.Request(url, datagen, headers)

        response = urllib2.urlopen(request)
        response = json.loads(response.read())
        if not response['success']:
            log.error('Derived file post failed: %s', response['message'])
    except urllib2.HTTPError as e:
        statsd.incr('failed_conversions')
        log.error('Failed to upload: %s - %s - %s', e.hdrs, e.code, e.msg)
        return False

    statsd.incr('successful_convertions')

    if callback:
        subtask(callback).delay()
    return True

@task(acks_late=True)
def create_pngs(document_pk, type='pngs', callback=None):
    doc = api.document(document_pk).get()
    log.info('Starting png generation of: %s', doc[u'title'])

    # Check to make sure that we don't already have a pngs pack
    for pack in doc[u'packs']:
        if pack[u'type'] == u'pngs':
            log.warn('a pngs pack aready exists for this document!')
            return False

    # Locate a pdf file
    pdf = None
    for pack in doc[u'packs']:
        if pack[u'type'] == u'pdf':
            pack = api.derivedpack(pack[u'id']).get()
            for file in pack[u'files']:
                if file[u'order'] == 0:
                    pdf = api.derivedfile(file[u'id']).get()
                    break
            break

    if not pdf:
        if doc[u'file'].endswith('.pdf'):
            pdf = doc

    if not pdf:
        log.error('Unable to generate pngs for %s because there is no pdf', doc[u'title'])
        return False

    # Get the file using the absolute url
    url = 'http://localhost' + pdf[u'download_url']

    req = requests.get(url, auth=auth)
    if req.status_code != 200:
        statsd.incr('failed_png_generations')
        log.warn('Did not get a HTTP 200 code when retrieving document.' +
            'Aborting convertion. Error Returned: %s - %s - %s',
            req.url, req.status_code, req.text)

        create_pdf.retry()

    # Create a temp folder
    temp_folder = tempfile.mkdtemp()
    log.debug('working with: %s', temp_folder)

    file = tempfile.NamedTemporaryFile(dir=temp_folder, delete=False)

    for data in req.iter_content(10240):
        file.write(data)
    file.close()

    # Now call ghostscript
    return_code = subprocess.call(["gs", "-sDEVICE=png16m",
        "-sOutputFile=%s/slide-%s.png" % (temp_folder, '%03d'),
        "-r600", "-dNOPAUSE", "-dBATCH", "-dMaxBitmap=1000000000",
        "-dFirstPage=1", "-dLastPage=1",
        "%s" % file.name])

    if return_code != 0:
        log.error('Ghostscript error')
        # Clean up
        shutil.rmtree(temp_folder)
        create_pngs.retry()

    # Process the generated files with PIL

    # First generate a list of file in the tempdir
    compiled_regex = re.compile('^slide-(\w+).png$')
    scaled_images = {}
    for file in os.listdir(temp_folder):
        # Check using regex
        match = re.match(compiled_regex, file)
        if match:
            log.debug('scaling image: %s', file)
            order = int(match.group(1))

            # Resize using PIL
            slide = Image.open(os.path.join(temp_folder, file))
            slide.thumbnail((1920, 1200), Image.ANTIALIAS)

            new_filename = os.path.join(temp_folder, 'slide-scaled-%03d.png' % order)
            slide.save(new_filename)
            scaled_images[order] = new_filename

    # Make sure that the order starts at 0 and has no gaps
    new_images = {}
    order = 0
    sorted_keys = scaled_images.keys()
    sorted_keys.sort()
    for item in [scaled_images[key] for key in sorted_keys]:
        new_images[order] = item
        order += 1
    scaled_images = new_images

    # Now go through all the generated slides and upload
    # Create a new derivedfile pack
    pack = api.derivedpack.post({"type": "pngs", "document": doc["resource_uri"]})
    for order, filename in scaled_images.iteritems():
        file = open(filename, 'rb')
        try:
            log.debug('attemping to upload: %s' % filename)
            url = "http://localhost/api/v1/document/%s/pack/%s/derived_file/" % (
                document_pk, pack["id"])

            datagen, headers = multipart_encode({
                'file': file, 'order':str(order)
            })

            request = urllib2.Request(url, datagen, headers)

            response = urllib2.urlopen(request)
            response = json.loads(response.read())

            if not response['success']:
                log.error('Derived file post failed: %s', response['message'])
        except urllib2.HTTPError as e:
            statsd.incr('failed_conversions')
            log.error('Failed to upload: %s - %s - %s - %s',
                filename, e.hdrs, e.code, e.msg)
        finally:
            file.close()

    shutil.rmtree(temp_folder)

    if callback:
        subtask(callback).delay()

    return True
