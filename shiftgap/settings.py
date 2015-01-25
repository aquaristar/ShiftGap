from os.path import join, abspath, dirname
from os import environ

here = lambda *dirs: join(abspath(dirname(__file__)), *dirs)

BASE_DIR = here('..')  # one directory up

root = lambda *dirs: join(abspath(BASE_DIR), *dirs)  # project directory

from django.utils.crypto import get_random_string
SECRET_KEY = environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if environ.get('DEBUG', 'false').lower() == 'true' else False

TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'shiftgap.urls'
WSGI_APPLICATION = 'shiftgap.wsgi.application'

ALLOWED_HOSTS = [x.strip() for x in environ.get('ALLOWED_HOSTS', '').split(',') if x]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_ID = 1

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.formtools',


    # all auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include the providers you want to enable:
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    # 'allauth.socialaccount.providers.github',

    # third party
    'djangosecure',
    'debug_toolbar',
    'timezone_field',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'django_twilio',
    'djcelery',

    # project apps
    'apps.ui',
    'apps.organizations',
    'apps.shifts',
    'apps.phone',
)

MIDDLEWARE_CLASSES = (
    'djangosecure.middleware.SecurityMiddleware',  # django-secure package
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    'django.contrib.admindocs.middleware.XViewMiddleware',  # for admindocs
    'apps.middleware.timezone.set_tz.SetUsersTimezoneMiddleware',
    'apps.middleware.timezone.set_tz.TimezoneMiddleware',
)

PRODUCTION = True if environ.get('PRODUCTION', 'false').lower() == 'true' else False

if PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': environ.get('SG_DB_NAME'),
            'USER': environ.get('SG_DB_USER'),
            'PASSWORD': environ.get('SG_DB_PASSWORD'),
            'HOST': environ.get('SG_DB_HOST'),
            'PORT': environ.get('SG_DB_PORT'),
            'CONN_MAX_AGE': 900,
            'OPTIONS': {
                'sslmode': 'verify-full',
                'sslrootcert': 'shiftgap/rds-ssl-ca-cert.pem'
            }
        },
        }
else:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config()
    }

DATABASES['default']['ATOMIC_REQUESTS'] = True


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    root('translations'),
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    root('static'),
    root('apps/ui/static'),
)

STATIC_ROOT = root('staticfiles')

# Template files
TEMPLATE_DIRS = (
    root('templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",  # not included by default but django-allauth needs it
    "django.contrib.messages.context_processors.messages",

    # project specific
    "apps.ui.context_processors.process_ui_views",

    # allauth specific context processors
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",

)

LOGIN_URL = '/login/'

LOGOUT_URL = '/logout/'

LOGIN_REDIRECT_URL = '/postlogin/'

SOCIALACCOUNT_PROVIDERS = {
    'facebook':
        {
            'SCOPE': ['email', 'publish_stream'],
            'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
            'METHOD': 'oauth2',
            'VERIFIED_EMAIL': False,
            'VERSION': 'v2.2'
        }
}

#  ################ EMAIL SETTINGS #######################
EMAIL_BACKEND = environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Email settings.
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = environ.get("SENDGRID_USERNAME", "")
EMAIL_HOST_PASSWORD = environ.get("SENDGRID_PASSWORD", "")
EMAIL_PORT = 25
EMAIL_USE_TLS = False

ADMINS = (('Enstrategic', 'info@enstrategic.com'), ('Mike', 'mike@eth0.ca'))
SERVER_EMAIL = 'info@enstrategic.com'

# So messages will work with bootstrap we need error to make danger
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.DEBUG: 'debug',
                message_constants.INFO: 'info',
                message_constants.SUCCESS: 'success',
                message_constants.WARNING: 'warning',
                message_constants.ERROR: 'danger', }


# AWS settings

# INSTALLED_APPS += ('storages',)  # if using django storages
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'  # if using django storages
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
AWS_CALLING_FORMAT = environ.get('AWS_CALLING_FORMAT')
AWS_QUERYSTRING_AUTH = False

# For maximum in browser caching
# AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
#                  'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
#                  'Cache-Control': 'max-age=94608000',
#                  }

# django-secure
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # redirect to SSL
    SECURE_FRAME_DENY = True  # don't allow display in frames
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

# Output logs to heroku logplex
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            },
        },
    "loggers": {
        "django": {
            "handlers": ["console"],
            }
    }
}

# run celery tasks synchronously during development
# CELERY_ALWAYS_EAGER = True if DEBUG else False
CELERY_ALWAYS_EAGER = True

REDIS_URL = environ.get('REDISCLOUD_URL', 'redis://localhost')
BROKER_URL = REDIS_URL
BROKER_TRANSPORT = 'redis'
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
#CELERY_RESULT_BACKEND = REDIS_URL + '/1'
CELERY_REDIS_MAX_CONNECTIONS = 2
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'


CORS_ORIGIN_ALLOW_ALL = True if DEBUG else False

TWILIO_DEFAULT_CALLERID = '+15874091230'