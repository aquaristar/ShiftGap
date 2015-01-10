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
    'django.contrib.sites',

    # third party
    'djangosecure',
    'debug_toolbar',

    # project apps
    'apps.ui',
)

MIDDLEWARE_CLASSES = (
    'djangosecure.middleware.SecurityMiddleware',  # django-secure package
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

    'django.contrib.admindocs.middleware.XViewMiddleware',  # for admindocs
)

PRODUCTION = True if environ.get('PRODUCTION', 'false').lower() == 'true' else False

if PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': environ.get('P_DB_NAME'),
            'USER': environ.get('P_DB_USER'),
            'PASSWORD': environ.get('P_DB_PASSWORD'),
            'HOST': environ.get('P_DB_HOST'),
            'PORT': environ.get('P_DB_PORT'),
            'CONN_MAX_AGE': 900,
            'OPTIONS': {
                'sslmode': 'verify-full',
                'sslrootcert': 'procedurized/rds-ssl-ca-cert.pem'
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

# Template files
TEMPLATE_DIRS = (
    root('templates'),
)

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

# Redis on Heroku
#REDIS_URL = environ.get('REDISTOGO_URL', 'redis://localhost')

# Using celery on Heroku must limit connections on free/starter plan
# JSON only is most secure
## BROKER_URL = REDIS_URL
#BROKER_TRANSPORT = 'redis'
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_ACCEPT_CONTENT = ['json']
#CELERY_RESULT_BACKEND = REDIS_URL + '/1'
#CELERY_REDIS_MAX_CONNECTIONS = 2

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
if PRODUCTION:
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
if not PRODUCTION:
    CELERY_ALWAYS_EAGER = True