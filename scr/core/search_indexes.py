from pysolr import Solr

from django.conf import settings

from haystack.indexes import *
from haystack import site
from core.models import Document


class DocumentIndex(RealTimeSearchIndex):
    text = CharField(document=True)
    title = CharField(model_attr='title', boost=1.125)
    #author = CharField(model_attr='user__get_full_name', faceted=True)
    #module = CharField(model_attr='module__get_full_title')

    def prepare(self, obj):
        data = super(DocumentIndex, self).prepare(obj)

        # Setup a solr instance for extract file contents
        solr = Solr(settings.SOLR_URL, timeout=20)

        # Get the file
        raw_file = obj.file

        extracted_data = solr.extract(raw_file)

        data['text'] = extracted_data['contents']
        return data

site.register(Document, DocumentIndex)
