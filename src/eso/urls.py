from django.conf.urls import patterns, include, url

from tastypie.api import Api
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

# from api.base import DocumentResource, DerivedPackResource, DerivedFileResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
#
# api_v1 = Api(api_name='v1')
# api_v1.register(DocumentResource())
# api_v1.register(DerivedPackResource())
# api_v1.register(DerivedFileResource())

sqs = SearchQuerySet().facet('tags')

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'core.views.home', name='home'),
    url(r'^thank-you/$', 'core.views.email_submit'),
    url(r'^upload/$', 'upload.views.new_upload'),
    url(r'^getdetails/$', 'upload.views.get_upload_details'),
    url(r'^preview/(\d+)?$', 'core.views.serve_document_thumbnail',
        name='preview'),
    url(r'^document/(\d+)/(?:(\w+)/)?(?:(\d+)/)?$', 'core.views.serve_document',
        name='serve_document'),

    url(r'^search/', FacetedSearchView(form_class=FacetedSearchForm, searchqueryset=sqs),
        name='haystack_search'),

    # Api urls
    # url(r'^api/v1/document/([0-9]+)/pack/([0-9]+)/derived_file/$',
    #       'core.views.api_derived_document_upload'),
    #   url(r'^api/v1/document/upload/$',
    #       'upload.views.api_document_upload_view'),
    #   url(r'^api/v1/download_document/(\d+)/(?:(\w+)/)?(?:(\d+)/)?$',
    #       'core.views.serve_document', name='api_serve_document'),
    #   url(r'^api/', include(api_v1.urls)),

    # Login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
