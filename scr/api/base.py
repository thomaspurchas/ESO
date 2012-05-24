from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import Authorization

from core.models import Document, DerivedFile, DerivedPack

class DocumentResource(ModelResource):
    packs = fields.ToManyField('api.base.DerivedPackReducedResource', 'packs',
        full=True)
    class Meta:
        queryset = Document.objects.all()
        resource_name = 'document'
        excludes = ['md5_sum']
        include_absolute_url = True

class DerivedPackResource(ModelResource):
    files = fields.ToManyField('api.base.DerivedFileResource', 'files',
        full=True, null=True)
    document = fields.ToOneField(DocumentResource, 'derived_from')
    class Meta:
        queryset = DerivedPack.objects.all()
        resource_name = 'derivedpack'
        excludes = []
        authorization= Authorization()

# A sub class of the above resource. This just makes sure that we dont send
# stupid amounts of info when a document is requested.
class DerivedPackReducedResource(DerivedPackResource):
    class Meta(DerivedPackResource.Meta):
        excludes = ['files', 'document']

class DerivedFileResource(ModelResource):
    class Meta:
        queryset = DerivedFile.objects.all()
        resource_name = 'derivedfile'
        excludes = ['md5_sum']
