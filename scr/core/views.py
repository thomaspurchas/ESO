# Create your views here.
from django.views.static import serve
from django.conf import settings

from core.models import Document

def serve_document(request, pk):
    doc = Document.objects.get(pk=pk)

    return serve(request, doc.file.name, settings.MEDIA_ROOT)
