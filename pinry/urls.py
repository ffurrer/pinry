from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
import allauth
from django.conf.urls.i18n import i18n_patterns


admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'', include('pinry.core.urls', namespace='core')),
    url(r'', include('pinry.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),
    #Admin Urls
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# urlpatterns += i18n_patterns('',
#     url(r'^about/$', About().view(), name='about'),
# )
urlpatterns += i18n_patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    # url(r'^license/$', 'flatpage', {'url': '/license/'}, name='license'),
)


js_info_dict = {
    'domain': 'djangojs',
    'packages': ('pinry',),
}

urlpatterns += i18n_patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

# urlpatterns += patterns('',
#     (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
# )

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                                }),
                            )