from pysolr import Solr

from django.conf import settings

from haystack import indexes
from haystack import site
from core.models import Document, DerivedFile
from celery.task import task

# Setup a solr instance for extract file contents
solr = Solr(settings.SOLR_URL, timeout=240)

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

        # Check to see if we have extracted and stored the file content in the DB
        # before. If not extract the content.
        if obj.extracted_content == None:

            # Pass both the original and the PDF version to solr.
            # Then commit whichever one returns the most raw data

            # Get the file
            raw_file = obj.file

            file_extracted_data = solr.extract(raw_file)['contents']

            # Store the data in the obj and save it
            obj.extracted_content = file_extracted_data

            obj.save()

        # Now get its PDF derived file and check that for extracted content
        pdf_derivedfiles = DerivedFile.objects.filter(pack__derived_from=obj
            ).filter(pack__type='pdf')

        if pdf_derivedfiles and (pdf_derivedfiles[0].extracted_content == None):
            pdf_derivedfile = pdf_derivedfiles[0]

            pdf_file = pdf_derivedfile.file
            pdf_extracted_data = solr.extract(pdf_file)['contents']

            pdf_derivedfile.extracted_content = pdf_extracted_data
            pdf_derivedfile.save()

        data['text'] = obj.extracted_content

        if pdf_derivedfiles:
            if len(pdf_derivedfiles[0].extracted_content) > len(obj.extracted_content):
                data['text'] = pdf_derivedfiles[0].extracted_content

        return data

site.register(Document, DocumentIndex)
