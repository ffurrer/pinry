import hashlib

from django.contrib.auth.models import User as BaseUser
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth.models import Permission


@receiver(user_signed_up)
def signup_cb(request, user, **kwargs):
    permissions = Permission.objects.filter(codename__in=['add_pin', 'add_image', 'add_like', 'del_like'])
    user.user_permissions = permissions


class User(BaseUser):
    @property
    def gravatar(self):
        return hashlib.md5(self.email).hexdigest()

    class Meta:
        proxy = True