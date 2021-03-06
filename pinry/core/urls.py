from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from tastypie.api import Api

from .api import (
    ImageResource,
    ThumbnailResource,
    PinResource,
    UserResource,
    LightBoxResource,
)
from .views import CreateImage, PinView


v1_api = Api(api_name='v1')
v1_api.register(ImageResource())
v1_api.register(ThumbnailResource())
v1_api.register(PinResource())
v1_api.register(UserResource())
v1_api.register(LightBoxResource())

admin.autodiscover()

urlpatterns = patterns('',
    url(
        r'^api/',
        include(v1_api.urls, namespace='api'),
    ),

    url(
        r'^pins/pin-form/$',
        TemplateView.as_view(template_name='core/pin_form.html'),
        name='pin-form',
    ),
    url(
        r'^pins/create-image/$',
        CreateImage.as_view(),
        name='create-image',
    ),

    url(
        r'^pins/tag/(?P<tag>(\w|-)+)/$',
        TemplateView.as_view(template_name='core/pins.html'),
        name='tag-pins',
    ),
    url(
        r'^pin/(?P<pinid>([0-9]+))/$',
        PinView.as_view(template_name='core/pins.html'),
        name='id-pin',
    ),
    url(
        r'^pins/user/(?P<user>(\w|-|\.)+)/$',
        TemplateView.as_view(template_name='core/pins.html'),
        name='user-pins',
    ),
    url(
        r'^$',
        PinView.as_view(template_name='core/pins.html'),
        name='recent-pins',
    ),
)
