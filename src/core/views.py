# Create your views here.
import logging
import os
from hashlib import md5
import json

import Image
from tastypie.authentication import DigestAuthentication

from django.conf import settings
from django.views.static import serve
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from utils import get_object_or_none
from core.models import Document, DerivedFile, DerivedPack, Email
from core.forms import ApiDerivedFileUploadForm, PostEmail

log = logging.getLogger(__name__)

def email_submit(request):
    if request.method == "POST":
        form = PostEmail(request.POST)
        if form.is_valid():
            if not Email.objects.filter(email=form.cleaned_data['email'].lower()):
                email = Email()
                email.email = form.cleaned_data['email'].lower()
                email.save()

            return render(request, 'thank-you.html')


    return HttpResponseRedirect('/search/')

def home(request):
    return HttpResponseRedirect('/search/')

def serve_document(request, pk, type=None, order=None):
    if request.path.startswith('/api/'):
        DigestAuthentication().is_authenticated(request)

    doc = get_object_or_404(Document, pk=pk)
    #pack = doc.packs.objects.get(type='pdf')
    object = None
    if type:
        type = str(type)
        if type.endswith('/'):
            type = type[:-1]
        if not order:
            order = '0'
        if order.endswith('/'):
            order = order[:-1]
        object = get_object_or_none(DerivedFile,
            pack__derived_from=doc, pack__type__exact=type, order=int(order))

        # If you document is a pdf and they want a pdf, serve the original
        if (type == 'pdf') and (not object) and (doc.file.name.lower().endswith('.pdf')):
            object = doc
    else:
        object = doc

    if not object:
        raise Http404

    return serve(request, object.file.name, settings.MEDIA_ROOT)

def serve_document_thumbnail(request, document_pk, width, format=None):
    if not format:
        format = settings.ALLOWED_IMAGE_FORMATS[0]
    if (width in settings.ALLOWED_IMAGE_WIDTHS) and (
        format in settings.ALLOWED_IMAGE_FORMATS):
        #get photo
        photo=get_object_or_404(DerivedFile, order=0,
            pack__type='pngs', pack__derived_from__id=document_pk)

        #path to original image and file split
        original_file=os.path.join(settings.MEDIA_ROOT,photo.file.name)
        filehead, filetail = os.path.split(original_file)

        filename, fileext = os.path.splitext(filetail)

        image_file = os.path.join(settings.IMAGE_ON_DEMAND_DIR, str(width),
            str(photo.pack.derived_from.id), format, filename + '.' + format)

        #check if image path exists otherwise create it
        image_path=os.path.dirname(image_file)
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        # check if file exists and the original file hasn't updated in between
        if os.path.exists(image_file) and os.path.getmtime(original_file)>os.path.getmtime(image_file):
            os.unlink(image_file)

        # if the image wasn't already resized, resize it.Maybe I should rewrite it to do this directly with PythonMagick
        # taken from snippet http://www.djangosnippets.org/snippets/453/

        if not os.path.exists(image_file):
            print 'image cache miss'
            image = Image.open(original_file)

            # we need te calculate the new height based on the ratio of the original image, create integers
            ratio=float(float(image.size[0]) / float(image.size[1]))
            height=int(float(width)/ratio)
            width=int(width)

            image.thumbnail((width, height), Image.ANTIALIAS)

            #optional unsharp mask using snippet http://www.djangosnippets.org/snippets/1267/
            #image = usm(image,settings.RADIUS,settings.SIGMA,settings.AMOUNT,settings.THRESHOLD)

            try:
                image.save(image_file, format, quality=90, optimize=1)
            except:
                image.save(image_file, format, quality=90)

        return serve(request, image_file, '/')

# A simple view that allows the upload of new derived files from worker machines
@csrf_exempt # Turn off csrf because its silly for an api.
def api_derived_document_upload(request, document_pk, pack_pk):

    if request.path.startswith('/api/'):
        DigestAuthentication().is_authenticated(request)

    if request.method == 'POST':
        log.debug('Derived File Post')
        # Process the request
        form = ApiDerivedFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)

            sum = md5()
            for chunk in new_file.file.chunks():
                sum.update(chunk)

            md5_sum =  sum.hexdigest()
            new_file.md5_sum = md5_sum

            if not Document.objects.unique_md5(md5_sum, (DerivedFile,)):

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

                    if not pack.derived_from == doc:
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
                            'success': True,
                            'message': 'the document does not exist'
                        }
                except DerivedPack.DoesNotExist:
                    response_data = {
                            'result': 'failure',
                            'success': True,
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
