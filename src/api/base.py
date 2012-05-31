from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import DigestAuthentication
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key

from core.models import Document, DerivedFile, DerivedPack

models.signals.post_save.connect(create_api_key, sender=User)

class DocumentResource(ModelResource):
    packs = fields.ToManyField('api.base.DerivedPackReducedResource', 'packs',
        full=True)
    download_url = fields.CharField(attribute='get_api_url', readonly=True, null=True)
    class Meta:
        queryset = Document.objects.all()
        resource_name = 'document'
        excludes = ['md5_sum']
        include_absolute_url = True
        authentication = DigestAuthentication()

class DerivedPackResource(ModelResource):
    files = fields.ToManyField('api.base.DerivedFileResource', 'files',
        full=True, null=True)
    document = fields.ToOneField(DocumentResource, 'derived_from')
    class Meta:
        queryset = DerivedPack.objects.all()
        resource_name = 'derivedpack'
        excludes = []
        authorization= Authorization() # CHANGE THIS!!

# A sub class of the above resource. This just makes sure that we dont send
# stupid amounts of info when a document is requested.
class DerivedPackReducedResource(DerivedPackResource):
    class Meta(DerivedPackResource.Meta):
        excludes = ['files', 'document']

class DerivedFileResource(ModelResource):
    pack = fields.ToOneField('api.base.DerivedPackReducedResource', 'pack')
    download_url = fields.CharField(attribute='get_api_url', readonly=True, null=True)
    class Meta:
        queryset = DerivedFile.objects.all()
        resource_name = 'derivedfile'
        excludes = ['md5_sum', 'file']
        include_absolute_url = True
        filtering = {
            'pack': ['exact'],
            'order': ['lte', 'gte', 'exact']
        }
