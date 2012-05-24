import logging
import mimetypes
import tempfile
import urllib2
import os
import json

import slumber
import requests
from django_statsd.clients import statsd
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from celery.task import task
from celery.task import Task
from celery.exceptions import WorkerLostError
# Setup logging and stats
log = logging.getLogger(__name__)
statsd

# Register the streaming http handlers with urllib2
register_openers()

# Celery tasks
api = slumber.API('http://localhost:8000/api/v1')

class AlwaysRetryTask(Task):

        def __call__(self, *args, **kwargs):
            try:
                return self.run(*args, **kwargs)
            except WorkerLostError, exc:
                self.retry(exc=exc)

@task(acks_late=True)
def create_pdf(document_pk, type='pdf'):
    doc = api.document(document_pk).get()
    log.info('Starting conversion of: %s', doc[u'title'])
    for pack in doc[u'packs']:
        if pack[u'type'] == u'pdf':
            log.info('DerivedPack with pdf type. Creation stopped')
            return True

    statsd.incr('attemped_conversions')

    # Get the file using the absolute url
    url = 'http://localhost:8000' + doc[u'absolute_url']

    req = requests.get(url)
    if req.status_code != 200:
        statsd.incr('failed_conversions')
        log.warn('Did not get a HTTP 200 code when retrieving document.' +
            'Aborting convertion. Error Returned: %s - %s', req.status_code, req.text)

        create_pdf.retry()

    if not 'content-type' in req.headers:
        statsd.incr('failed_conversions')
        log.error('No mime type returned will document request')
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

        url = "http://localhost:8000/api/v1/document/%s/pack/%s/derived_file/" % (
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
    return True
