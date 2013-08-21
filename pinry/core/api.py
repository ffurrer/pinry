from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import Unauthorized, ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from django.conf.urls import url
from django_images.models import Thumbnail

from .models import Pin, Image, Like
from ..users.models import User


class PinryAuthorization(DjangoAuthorization):
    """
    Pinry-specific Authorization backend with object-level permission checking.
    """
    def update_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission = '%s.change_%s' % (klass._meta.app_label, klass._meta.module_name)

        if not bundle.request.user.has_perm(permission, bundle.obj):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def delete_detail(self, object_list, bundle):
        klass = self.base_checks(bundle.request, bundle.obj.__class__)

        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")

        permission = '%s.delete_%s' % (klass._meta.app_label, klass._meta.module_name)

        if not bundle.request.user.has_perm(permission, bundle.obj):
            raise Unauthorized("You are not allowed to access that resource.")

        return True


class UserResource(ModelResource):
    gravatar = fields.CharField(readonly=True)

    def dehydrate_gravatar(self, bundle):
        return bundle.obj.gravatar

    class Meta:
        list_allowed_methods = ['get']
        filtering = {
            'username': ALL
        }
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username']
        include_resource_uri = False


def filter_generator_for(size):
    def wrapped_func(bundle, **kwargs):
        return bundle.obj.get_by_size(size)
    return wrapped_func


class ThumbnailResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        fields = ['image', 'width', 'height']
        queryset = Thumbnail.objects.all()
        resource_name = 'thumbnail'
        include_resource_uri = False


class ImageResource(ModelResource):
    standard = fields.ToOneField(ThumbnailResource, full=True,
                                 attribute=lambda bundle: filter_generator_for('standard')(bundle))
    thumbnail = fields.ToOneField(ThumbnailResource, full=True,
                                  attribute=lambda bundle: filter_generator_for('thumbnail')(bundle))
    square = fields.ToOneField(ThumbnailResource, full=True,
                               attribute=lambda bundle: filter_generator_for('square')(bundle))

    class Meta:
        fields = ['image', 'width', 'height']
        include_resource_uri = False
        resource_name = 'image'
        queryset = Image.objects.all()
        authorization = DjangoAuthorization()

class LikeResource(ModelResource):
    #pin = fields.ForeignKey('pinry.core.api.PinResource', 'pin')
    
    #user = fields.ForeignKey(UserResource, 'user')
    #pin = fields.ForeignKey('PinResource', 'pin')

    def obj_create(self, bundle, **kwargs):
        pin = Pin.objects.get(pk=kwargs['pk'])
        likes = Like.objects.filter(pin=pin, user=bundle.request.user)
        if likes.exists():
            raise ImmediateHttpResponse(http.HttpConflict("You are not allowed to like this Pin multiple times."))
        return super(LikeResource, self).obj_create(bundle, pin=pin, user=bundle.request.user)

    def obj_delete_list(self, bundle, **kwargs):
        pin = Pin.objects.get(pk=kwargs['pk'])

        like = self.obj_get(bundle, pin=pin, user=bundle.request.user)
        return super(LikeResource, self).obj_delete_list(bundle, pin=pin, user=bundle.request.user)

    def dehydrate(self, bundle):
        return Like.objects.count()
    
    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

    class Meta:
        queryset = Like.objects.all()
        #resource_name = 'like'
        #fields = ['user', 'pin', 'liked']
        allowed_methods = ['get', 'post', 'delete']
        always_return_data = True
        authorization = PinryAuthorization()


class PinResource(ModelResource):
    submitter = fields.ToOneField(UserResource, 'submitter', full=True)
    image = fields.ToOneField(ImageResource, 'image', full=True)
    tags = fields.ListField()
    like_count = fields.IntegerField(readonly=True)
    liked = fields.BooleanField(readonly=True)
    #likes = fields.ToManyField(LikeResource, lambda bundle: Like.objects.filter(pin=bundle.obj), full=True, null=True)
    likes = fields.ToManyField(LikeResource, 'likes', full=False, null=True)

    def hydrate_image(self, bundle):
        url = bundle.data.get('url', None)
        if url:
            image = Image.objects.create_for_url(url)
            bundle.data['image'] = '/api/v1/image/{}/'.format(image.pk)
        return bundle

    def hydrate(self, bundle):
        """Run some early/generic processing

        Make sure that user is authorized to create Pins first, before
        we hydrate the Image resource, creating the Image object in process
        """
        submitter = bundle.data.get('submitter', None)
        if not submitter:
            bundle.data['submitter'] = '/api/v1/user/{}/'.format(bundle.request.user.pk)
        else:
            if not '/api/v1/user/{}/'.format(bundle.request.user.pk) == submitter:
                raise Unauthorized("You are not authorized to create Pins for other users")
        return bundle

    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())

    def dehydrate_like_count(self, bundle):
        return bundle.obj.like_set.filter(pin=bundle.obj).count()

    def dehydrate_liked(self, bundle):
        return bundle.obj.like_set.filter(user=bundle.request.user).exists()

    def prepend_urls(self): # prepend_urls in 0.9.12
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/likes%s$' % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_likes'),
                name='api_parent_likes'),
        ]

    def dispatch_likes(self, request, **kwargs):
        return LikeResource().dispatch('list', request, **kwargs)

    """
    def dehydrate_likes(self, bundle):
        return 4
    """

    def build_filters(self, filters=None):
        orm_filters = super(PinResource, self).build_filters(filters)
        if filters and 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].split(',')
        return orm_filters

    def save_m2m(self, bundle):
        tags = bundle.data.get('tags', None)
        if tags:
            bundle.obj.tags.set(*tags)
        return super(PinResource, self).save_m2m(bundle)

    class Meta:
        fields = ['id', 'url', 'origin', 'description']
        ordering = ['id']
        filtering = {
            'submitter': ALL_WITH_RELATIONS
        }
        queryset = Pin.objects.all()
        resource_name = 'pin'
        include_resource_uri = False
        always_return_data = True
        authorization = PinryAuthorization()
