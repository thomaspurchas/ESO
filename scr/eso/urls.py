from django.conf.urls import patterns, include, url

from tastypie.api import Api

from api.base import DocumentResource, DerivedPackResource, DerivedFileResource

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

api_v1 = Api(api_name='v1')
api_v1.register(DocumentResource())
api_v1.register(DerivedPackResource())
api_v1.register(DerivedFileResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eso.views.home', name='home'),
    # url(r'^eso/', include('eso.foo.urls')),
    url(r'^upload/$', 'upload.views.new_upload'),
    url(r'^getdetails/$', 'upload.views.get_upload_details'),
    url(r'^document/(\d+)/$', 'core.views.serve_document'),

    (r'^search/', include('haystack.urls')),

    # Api urls
    url(r'^api/v1/document/([0-9]+)/pack/([0-9]+)/derived_file/$',
        'core.views.api_derived_document_upload'),
    url(r'^api/', include(api_v1.urls))

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
