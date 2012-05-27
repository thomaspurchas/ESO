from django.conf.urls import patterns, include, url

from tastypie.api import Api
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from api.base import DocumentResource, DerivedPackResource, DerivedFileResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

api_v1 = Api(api_name='v1')
api_v1.register(DocumentResource())
api_v1.register(DerivedPackResource())
api_v1.register(DerivedFileResource())

sqs = SearchQuerySet().facet('tags')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eso.views.home', name='home'),
    # url(r'^eso/', include('eso.foo.urls')),
    url(r'^upload/$', 'upload.views.new_upload'),
    url(r'^getdetails/$', 'upload.views.get_upload_details'),
    url(r'^document/(\d+)/thumbnail/(\d+)/(?:(\w+)/)?$', 'core.views.serve_document_thumbnail',
        name='serve_document_thumbnail'),
    url(r'^document/(\d+)/(?:(\w+)/)?(?:(\d+)/)?$', 'core.views.serve_document',
        name='serve_document'),

    url(r'^search/', FacetedSearchView(form_class=FacetedSearchForm, searchqueryset=sqs),
        name='haystack_search'),

    # Api urls
    url(r'^api/v1/document/([0-9]+)/pack/([0-9]+)/derived_file/$',
        'core.views.api_derived_document_upload'),
    url(r'^api/', include(api_v1.urls)),

    # Login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
