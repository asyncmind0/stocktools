from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'web.views.index', name='index'),
    url(r'^symbols$', 'web.views.get_symbols', name='get_symbols'),
    url(r'^sectors$', 'web.views.get_sectors', name='get_sectors'),
    url(r'^loosers52$', 'web.views.get_loosers52', name='get_loosers52'),
    url(r'^info/(?P<symbol>\w+)$', 'web.views.get_info', name='get_info'),
    url(r'^updatedb$', 'web.documents.views.updatedb', name='updatedb'),
    url(r'^stockinfo/(?P<symbol>\w+)/(?P<date>\d*)$', 'web.documents.views.stockinfo', name='stockinfo'),
)
