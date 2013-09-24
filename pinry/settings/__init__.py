import os

from django.contrib.messages import constants as messages
# from django.utils.translation import ugettext as _

_ = ugettext = lambda x: x

SITE_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), '../../')


# Changes the naming on the front-end of the website.
SITE_NAME = 'Striplac Style of the Year'

# Set to False to disable people from creating new accounts.
ALLOW_NEW_REGISTRATIONS = True

# Set to False to force users to login before seeing any pins. 
PUBLIC = True
LANGUAGE_CODE = 'de'

LANGUAGES = (
  ('de', _('German')),
  ('en', _('English')),
)

TIME_ZONE = 'America/New_York'

USE_I18N = True
USE_L10N = True
USE_TZ = True

TASTYPIE_FULL_DEBUG = True


MEDIA_URL = '/media/'
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
TEMPLATE_DIRS = [os.path.join(SITE_ROOT, 'pinry/templates')]
STATICFILES_DIRS = [os.path.join(SITE_ROOT, 'pinry/static')]

CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=60'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pinry.users.middleware.Public',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'pinry.core.context_processors.template_settings',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
)
AUTHENTICATION_BACKENDS = (
    'pinry.users.auth.backends.CombinedAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

LOCALE_PATHS = (
    os.path.join(SITE_ROOT, 'pinry/locale'),
)

ROOT_URLCONF = 'pinry.urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
INTERNAL_IPS = ['127.0.0.1']
MESSAGE_TAGS = {
    messages.WARNING: 'alert',
    messages.ERROR: 'alert alert-error',
    messages.SUCCESS: 'alert alert-success',
    messages.INFO: 'alert alert-info',
}
API_LIMIT_PER_PAGE = 50

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'south',
    'taggit',
    'compressor',
    'django_images',
    'pinry',
    'pinry.core',
    'pinry.users',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # include the providers you want to enable:
    # 'allauth.socialaccount.providers.bitly',
    # 'allauth.socialaccount.providers.dropbox',
    'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.github',
    # 'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.linkedin',
    # 'allauth.socialaccount.providers.openid',
    # 'allauth.socialaccount.providers.persona',
    # 'allauth.socialaccount.providers.soundcloud',
    # 'allauth.socialaccount.providers.stackexchange',
    # 'allauth.socialaccount.providers.twitch',
    # 'allauth.socialaccount.providers.twitter',
    # 'allauth.socialaccount.providers.vimeo',
    # 'allauth.socialaccount.providers.weibo',
)

SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_PROVIDERS = (
    { 
    'facebook':
        { 'SCOPE': ['email'],
          # 'AUTH_PARAMS': { 'auth_type': 'reauthenticate' },
          'METHOD': 'oauth2',  # 'js_sdk',  # ,
          'LOCALE_FUNC': lambda request: 'de'} 
    }
)

IMAGE_PATH = 'pinry.core.utils.upload_path'
IMAGE_SIZES = {
    'thumbnail': {'size': [240, 0]},
    'standard': {'size': [600, 0]},
    'square': {'crop': True, 'size': [125, 125]},
}


# AUTH_USER_MODEL = 'pinry.users.models.User'