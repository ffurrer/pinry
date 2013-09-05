import requests
from cStringIO import StringIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models, transaction

from django_images.models import Image as BaseImage, Thumbnail
from taggit.managers import TaggableManager

from ..users.models import User


class ImageManager(models.Manager):
    # FIXME: Move this into an asynchronous task
    def create_for_url(self, url):
        file_name = url.split("/")[-1]
        buf = StringIO()
        response = requests.get(url)
        buf.write(response.content)
        obj = InMemoryUploadedFile(buf, 'image', file_name,
                                   None, buf.tell(), None)
        # create the image and its thumbnails in one transaction, removing
        # a chance of getting Database into a inconsistent state when we
        # try to create thumbnails one by one later
        image = self.create(image=obj)
        return image


class Image(BaseImage):
    objects = ImageManager()

    class Meta:
        proxy = True

    def admin_image(self):
        return '<img src="/media/%s" style="height:50px;"/>' % self.get_by_size('thumbnail').image
    admin_image.allow_tags = True


class Pin(models.Model):
    submitter = models.ForeignKey(User)
    url = models.URLField(null=True)
    origin = models.URLField(null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ForeignKey(Image, related_name='pin')
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def __unicode__(self):
        return u"%s" % self.id
        # return u"%s" % (self.url if self.url is not None else "id: %s" % self.id)


class Like(models.Model):
    user = models.ForeignKey(User)
    pin = models.ForeignKey(Pin)
    liked = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"User <%s> liked Pin <%s> at <%s>" % (self.user.id, self.pin, self.liked)


class LightBox(models.Model):
    title = models.TextField()
    content = models.TextField(blank=True, null=True)
    link = models.URLField(null=True)
    description = models.TextField(blank=True, null=True)
    published = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(Image, related_name='lightbox')

    def admin_image(self):
        return '<img src="/media/%s" style="height:50px;"/>' % self.image.get_by_size('thumbnail').image
    admin_image.allow_tags = True

    def __unicode__(self):
        return u"%s" % self.title


def image_saved(sender, instance, created, **kwargs):
    if created and isinstance(instance, Image):
        for size in settings.IMAGE_SIZES.keys():
            Thumbnail.objects.get_or_create_at_size(instance.pk, size)

models.signals.post_save.connect(image_saved)
