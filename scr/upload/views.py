# Create your views here.
from pysolr import Solr

from django.conf import settings

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from upload.forms import NewUploadForm
from upload.forms import UploadDetailForm
from core.models import Document

def new_upload(request):
    # Generate and return a simple upload page

    form = NewUploadForm()

    return render_to_response('upload/new_upload.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

def get_upload_details(request):
    # Handle the file upload
    if request.method == 'POST':
        form = NewUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a new document object.
            new_document = Document(file = request.FILES['upload_file'])

            # Setup a solr instance for extract file contents
            solr = Solr(settings.SOLR_URL, timeout=20)

            file_data = solr.extract(new_document.file)
            print file_data['metadata']
            data = {}

            try:
                data['title'] = file_data['metadata']['title'][0]
                data['filename'] = file_data['metadata']['stream_name'][0]
                data['author'] = file_data['metadata']['Author'][0]
            except:
                pass

            details_form = UploadDetailForm(data)

            # Redirect the user to the upload information page after POST
            return render_to_response('upload/upload_details.html',
                {'form': details_form, 'file_name': data['filename']},
                context_instance=RequestContext(request)
            )

    # If we got here without a file
    print request.POST
    print request.FILES
    print request.method
    print form.is_valid()
    return HttpResponseRedirect(reverse('upload.views.new_upload'))
