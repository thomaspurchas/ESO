# Create your views here.
from hashlib import md5
from pysolr import Solr, SolrError
from os import path
import logging
import json

from tastypie.authentication import DigestAuthentication

from django_statsd.clients import statsd

from django.conf import settings

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from upload.forms import NewUploadForm, UploadDetailForm, ApiDocumentUploadForm
from core.models import Document, DerivedFile
from upload.models import TempFile
from convert.tasks import create_pdf, create_pngs

log = logging.getLogger(__name__)

# Setup a solr instance for extract file contents
solr = Solr(settings.SOLR_URL, timeout=20)

def clean_temp_file(file):
    # Helper function to clean up temp files
    file.file.delete()
    file.delete()

@csrf_exempt
def api_document_upload_view(request):
    if request.path.startswith('/api/'):
        DigestAuthentication().is_authenticated(request)

    if request.method == 'POST':
        log.debug('Document Post')
        # Process the request
        form = ApiDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)

            with statsd.timer('upload.md5_calc_time'):
                sum = md5()
                for chunk in new_file.file.chunks():
                    sum.update(chunk)

                md5_sum = sum.hexdigest()
                new_file.md5_sum = md5_sum

            new_file.title = new_file.file.name

            if not Document.objects.unique_md5(md5_sum, (DerivedFile,)):

                response_data = {
                        'result': 'failure',
                        'success': False,
                        'message': 'file already uploaded'
                    }
            else:
                new_file.save()
                # Create a PDF and pngs
                create_pdf.delay(new_file.id,
                    callback=create_pngs.subtask((new_file.id,)))
                response_data = {
                    'result': 'success',
                    'success': True,
                    'message': 'File uploaded'
                }
        else:
            response_data = {
                'result': 'failure',
                'success': False,
                'message': 'invalid form'
            }
    else:
        response_data = {
            'result': 'failure',
            'success': False,
            'message': 'you need to send me something!'
        }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

@login_required
def new_upload(request):
    # Generate and return a simple upload page

    form = NewUploadForm()
    if request.method == 'POST':
        form = NewUploadForm(request.POST, request.FILES)
        if form.is_valid():

            # Get the uploaded file and store it in a temporary storage location till
            # we can query the user for more information.
            temp_file = TempFile(file = request.FILES['upload_file'])
            temp_file.name = request.FILES['upload_file'].name

            # Create the md5 sum of the file, and time is
            with statsd.timer('upload.md5_calc_time'):
                sum = md5()
                for chunk in temp_file.file.chunks():
                    sum.update(chunk)

                temp_file.md5_sum = sum.hexdigest()

            # First check that we dont already have a copy of the file
            if not Document.objects.unique_md5(temp_file.md5_sum, (DerivedFile,)):
                log.debug('File was uploaded that we already have (md5: %s)',
                    temp_file.md5_sum)
                clean_temp_file(temp_file)
                return render_to_response('upload/new_upload.html',
                    {'form': form, 'error': 'File aready uploaded'},
                    #context_instance=RequestContext(request)
                )
            else:
                temp_file.save()

            # Store a ref to the db entry that looks after the temp file
            # But first check to see if there is already a temp file for this session
            if request.session.get('upload_file', False):
                # Delete the previous file
                request.session['upload_file'].delete()
            request.session['upload_file'] = temp_file

            # Redirect the user to a page where they can add useful information.
            return HttpResponseRedirect(reverse('upload.views.get_upload_details'))

    return render_to_response('upload/new_upload.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

@login_required
def get_upload_details(request):
    # Handle the file upload
    if request.method == 'POST':
        form = UploadDetailForm(request.POST)

        # Check the form is valid, and that we have a file to work with
        if form.is_valid() and request.session.get('upload_file', False):
            # Get the information that we stored on the file
            temp_file = request.session['upload_file']
            temp_file_sum = temp_file.md5_sum

            # Generate a document instance from the details the user provided
            new_document = Document(md5_sum = temp_file_sum)
            new_document.file.save(temp_file.name, temp_file.file, False)

            new_document.title = form.cleaned_data['title']

            # Save the document and clean up temp files and stuff
            new_document.save()
            log.info("Saved a new document: %s", new_document.id)
            clean_temp_file(temp_file)
            del request.session['upload_file']

            # Create a PDF and pngs
            create_pdf.delay(new_document.id,
                callback=create_pngs.subtask((new_document.id,)))

    if request.session.get('upload_file', False):
        temp_file = request.session['upload_file']

        data = {'filename': temp_file.name}

        try:
            try:
                file_data = solr.extract(temp_file.file)
            except IOError, e:
                log.warn('Solr extraction failed: %s', e)
                file_data = {'metadata': None}
            log.debug(file_data['metadata'])

            try:
                if file_data['metadata']:
                    data['title'] = file_data['metadata']['title'][0] or data['filename']
                    data['author'] = file_data['metadata']['Author'][0]
            except:
                pass

            data['title'] = data['filename']

            details_form = UploadDetailForm(data)

            # Redirect the user to the upload information page after POST
            return render_to_response('upload/upload_details.html',
                {'form': details_form, 'file_name': data['filename']},
                context_instance=RequestContext(request)
            )
        except SolrError:
            # Return an error message
            return render_to_response('upload/upload_details.html',
                {'error': 'Solr extraction error', 'file_name': data['filename']},
                context_instance=RequestContext(request)
            )


    # If we got here without a file, redirect to the upload page
    return HttpResponseRedirect(reverse('upload.views.new_upload'))
