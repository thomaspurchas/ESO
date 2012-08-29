import logging

from django.conf import settings

from celery_haystack.indexes import CelerySearchIndex
from haystack import indexes
from haystack import site
from core.models import Page
from celery.task import task

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

class PageIndex(indexes.SearchIndex):
    text = indexes.CharField(model_attr='body', document=True)
    url = indexes.CharField(model_attr='url')
    tags = indexes.MultiValueField(faceted=True)

    def prepare_tags(self, obj):
        return [tag.title for tag in obj.tags.all()]

    def prepare(self, obj):
        log.info('Indexing: %s - %s', obj.id, obj.url)

        data = super(PageIndex, self).prepare(obj)

        soup = BeautifulSoup(data['text'])

        # Strip out scripts
        for script in soup.find_all('script'):
            script.clear()

        # Get text and normalise
        text = ''
        for item in soup.find_all(text=True):
            item = item.strip()
            if item:
                text += ' ' + item

        data['text'] = text

        data['tags'].append(obj.site.title)

        return data

site.register(Page, PageIndex)
