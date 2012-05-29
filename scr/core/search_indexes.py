from pysolr import Solr

from django.conf import settings

from haystack import indexes
from haystack import site
from core.models import Document, DerivedFile


class DocumentIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr='title', boost=1.125)
    tags = indexes.MultiValueField(faceted=True)
    #author = CharField(model_attr='user__get_full_name', faceted=True)
    #module = CharField(model_attr='module__get_full_title')

    def prepare_tags(self, obj):
        return [tag.title for tag in obj.tags.all()]

    def prepare(self, obj):
        data = super(DocumentIndex, self).prepare(obj)

        # Setup a solr instance for extract file contents
        solr = Solr(settings.SOLR_URL, timeout=240)

        # Pass both the original and the PDF version to solr.
        # Then commit whichever one returns the most raw data

        # Get the file
        raw_file = obj.file

        file_extracted_data = solr.extract(raw_file)['contents']

        # Get PDF
        pdf_file_query = DerivedFile.objects.filter(pack__derived_from=obj)
        pdf_file_query = pdf_file_query.filter(pack__type='pdf')

        if len(pdf_file_query):
            pdf_file = pdf_file_query[0].file
            pdf_extracted_data = solr.extract(pdf_file)['contents']
        else:
            pdf_extracted_data = ''

        if len(pdf_extracted_data) >  len(file_extracted_data):
            data['text'] = pdf_extracted_data
        else:
            data['text'] = file_extracted_data

        for tag in obj.tags.all():
            data['text'] += ' ' + tag.title

        return data

site.register(Document, DocumentIndex)
