# Create your views here.
from hashlib import md5
import json

from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import Document, DerivedFile, DerivedPack
from core.forms import ApiDerivedFileUploadForm

def serve_document(request, pk):
    doc = Document.objects.get(pk=pk)

    return serve(request, doc.file.name, settings.MEDIA_ROOT)

# A simple view that allows the upload of new derived files from worker machines
@csrf_exempt # Turn off csrf because its silly for an api.
def api_derived_document_upload(request, document_pk, pack_pk):

    # Basic auth for later
    #if not getattr(request.META['REMOTE_USER'], False) == USER:
    #    return

    if request.method == 'POST':
        print 'got post'
        # Process the request
        form = ApiDerivedFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)

            sum = md5()
            for chunk in new_file.file.chunks():
                sum.update(chunk)

            md5_sum =  sum.hexdigest()
            new_file.md5_sum = md5_sum

            if not Document.objects.unique_md5(md5_sum):

                response_data = {
                        'result': 'failure',
                        'success': False,
                        'message': 'file already uploaded'
                    }
            else:
                try:
                    # Try looking up the relevant pack and document
                    doc = Document.objects.get(pk=int(document_pk))
                    pack = DerivedPack.objects.get(pk=int(pack_pk))

                    if not doc.derivedpack == pack:
                        response_data = {
                            'result': 'failure',
                            'success': False,
                            'message': 'document and pack did not match'
                        }
                    else:
                        new_file.pack = pack
                        new_file.save()
                        response_data = {
                            'result': 'success',
                            'success': True,
                            'message': sum.hexdigest()
                        }
                except Document.DoesNotExist:
                    response_data = {
                            'result': 'failure',
                            'success': false,
                            'message': 'the document does not exist'
                        }
                except DerivedPack.DoesNotExist:
                    response_data = {
                            'result': 'failure',
                            'success': false,
                            'message': 'the pack does not exist'
                        }

            return HttpResponse(json.dumps(response_data), mimetype="application/json")

        response_data = {
            'result': 'failure',
            'success': False,
            'message': 'form did not validate'
        }

        return HttpResponse(json.dumps(response_data), mimetype="application/json")

    response_data = {
        'result': 'failure',
        'success': False,
        'message': 'only post is allowed'
    }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")
