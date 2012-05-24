# Create your views here.
from hashlib import md5
from pysolr import Solr, SolrError
from os import path
import logging

from django.conf import settings

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from upload.forms import NewUploadForm
from upload.forms import UploadDetailForm
from core.models import Document, DerivedFile
from upload.models import TempFile
from pdfconvert.tasks import create_pdf

log = logging.getLogger(__name__)

def clean_temp_file(file):
    # Helper function to clean up temp files
    file.file.delete()
    file.delete()


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

            # Create the md5 sum of the file
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
                    context_instance=RequestContext(request)
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

            # Create a PDF
            log.info(create_pdf.delay(new_document.id).result)

    if request.session.get('upload_file', False):
        temp_file = request.session['upload_file']

        # Setup a solr instance for extract file contents
        solr = Solr(settings.SOLR_URL, timeout=20)
        data = {'filename': temp_file.name}

        try:
            file_data = solr.extract(temp_file.file)
            log.debug(file_data['metadata'])

            try:
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
