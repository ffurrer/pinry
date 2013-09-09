from django.core.validators import email_re

from pinry.core.models import Pin
from pinry.users.models import User


class CombinedAuthBackend(object):
    def authenticate(self, username=None, password=None):
        is_email = email_re.match(username)
        if is_email:
            qs = User.objects.filter(email=username)
        else:
            qs = User.objects.filter(username=username)

        try:
            user = qs.get()
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def has_perm(self, user, perm, obj=None):
        """
        Check if a user is authorized to do an operation on a pin.

        Args:
            user: django.contrib.auth.models.User object
            perm: string of the permission
            obj: pinry.core.models.Pin object if operating on a existing Pin
                 (default: None)
        Returns:
            True if user is authorized False otherwise
        """
        if obj and isinstance(obj, Pin):
            #TODO(ff): check if this is done nicely
            if (
                len(
                    user.user_permissions.filter(
                        codename=perm.split('.')[-1]
                    )
                ) == 1
                and obj.submitter.username == user.username
            ):
                return True
            # return obj.submitter.username == user.username
        return False
