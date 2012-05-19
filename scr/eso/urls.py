from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eso.views.home', name='home'),
    # url(r'^eso/', include('eso.foo.urls')),
    url(r'^upload/$', 'upload.views.new_upload'),
    url(r'^getdetails/$', 'upload.views.get_upload_details'),
    url(r'^document/(\d+)/$', 'core.views.serve_document'),
    url(r'^api/document/([0-9]+)/pack/([0-9]+)/derived_file/$',
        'core.views.api_derived_document_upload'),
    (r'^search/', include('haystack.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
