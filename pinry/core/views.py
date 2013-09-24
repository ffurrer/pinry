from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django_images.models import Image

from braces.views import JSONResponseMixin, LoginRequiredMixin
from django_images.models import Thumbnail

from .forms import ImageForm
from .models import Pin

DEFAULT_TEMPLATE = 'flatpages/default.html'

class CreateImage(JSONResponseMixin, LoginRequiredMixin, CreateView):
    template_name = None  # JavaScript-only view
    model = Image
    form_class = ImageForm

    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect(reverse('core:recent-pins'))
        return super(CreateImage, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        image = form.save()
        for size in settings.IMAGE_SIZES.keys():
            Thumbnail.objects.get_or_create_at_size(image.pk, size)
        return self.render_json_response({
            'success': {
                'id': image.id
            }
        })

    def form_invalid(self, form):
        return self.render_json_response({'error': form.errors})

class PinView(TemplateView):
    def get(self, request, *args, **kwargs):
        response = super(PinView, self).get(request, *args, **kwargs)

        # extra query in case the URL pints directly to a pin
        if 'pinid' in kwargs:
            pin = Pin.objects.get(id=kwargs['pinid'])
            response.context_data['image_url'] = pin.image.image
            response.context_data['image_description'] = pin.description

        # prize_view set to True (show overlay)
        if 'prize_view' in request.COOKIES and request.COOKIES['prize_view'] == 'True':
            response.context_data[u'prize_view'] = True
            response.set_cookie(
                key='prize_view',
                value=False,
            )
            return response
        if 'prize_view' in request.COOKIES and request.COOKIES['prize_view'] == 'False':
            response.context_data[u'prize_view'] = False
            response.set_cookie(
                key='prize_view',
                value=False,
            )
            return response
        # prize_view in args, set the cookie and (maybe show overlay)
        if 'prize_view' in args:
            response.context_data[u'prize_view'] = args['prize_view']
            response.set_cookie(
                key='prize_view',
                value=args['prize_view'],
            )
            return response
        # else no cookie exists
        else:
            response.context_data[u'prize_view'] = True
            response.set_cookie(
                key='prize_view',
                value=False,
            )
            return response
