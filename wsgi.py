import os
import sys


def here(*path):
    absolute_here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(absolute_here, *path)

sys.path.insert(0, here())


activate_this = here('..', 'env', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pinry.settings.development")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
