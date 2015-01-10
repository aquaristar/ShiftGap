enstrategic boilerplate
========================

* Django 1.7
* HTML5 boilerplate
* Bootstrap
* Jquery
* Modernizr


Search for all instances of 'rename-me' and rename them to your desired project name.

To create a custom settings file, create a new file in the settings subdirectory

> from .base import *

Then define your custom settings. Set environment variable DJANGO_SETTINGS_MODULE to your new settings file

Templates
=========
* ___ (three underscore) - template is meant to be a base (i.e. copied and pasted then renamed)
* __ (two underscores) - template is meant to be extended
* _ (one underscore) - template is meant to be included (not used on its own)
* (no underscores) - template is meant for end use

Improving site security
=======================

* Ideally, you should not store your site's ``SECRET_KEY`` setting in version control. Instead, it should be read
from the Heroku config as follows:

>    from django.utils.crypto import get_random_string
>    SECRET_KEY = os.environ.get("SECRET_KEY", get_random_string(50, "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"))

* You can then generate a secret key in your Heroku config with the following command:

>    $ heroku config:set SECRET_KEY=`openssl rand -base64 32`

* It's also recommended that you configure Python to generate a new random seed every time it boots.

>    $ heroku config:set PYTHONHASHSEED=random

Default Settings
================
**Warning:** Admin may be unaccessible due to django_secure settings. Consult documentation for more info.

You can try disabling these settings:

>   SECURE_SSL_REDIRECT = True # redirect to SSL

>   SECURE_FRAME_DENY = True # don't allow display in frames

>   SECURE_CONTENT_TYPE_NOSNIFF = True

>   SECURE_BROWSER_XSS_FILTER = True

>   SESSION_COOKIE_SECURE = True

>   SESSION_COOKIE_HTTPONLY = True



i18n & i10n
===========
Under rename-me/urls.py
* Uncomment i18n settings

ugettext vs ugettext_lazy generally

* ugettext_lazy in models & forms
* ugettext in views

LOCALE_PATHS in rename-me/settings/base.py is currently set to project_root/translations.

IMPORTANT
=========
Preferred coding styles/patterns:

* Prefer class based views where appropriate
* Always assume the project will be translated and at the very least use ugettext/ugettext_lazy for all python strings and 'trans' template blocks
* Configuration in environment variables or outside the repository
* Requirements must be specified in requirements.txt
* Portability is important (we should be able to switch hosting environments rapidly)
* All django apps specific to this project should go in apps/*
* All middleware specific to this project in middleware/*
* DO NOT extend the django.contrib.auth.User model - create a user profile and link to it using a OneToOne foreign key

Heroku
======
Heroku is great and we like launching new projects on it. Simple and easy to get going fast.

But the costs can add up, particularly of the add on features. Heroku is also in a single US AWS region. Enjoy the convenience of Heroku but plan to be able to move your code to a different environment without too much effort.

Money
=====
For anything financial in nature, make sure you use the Decimal data type. Please consult a product manager
for more information about required accuracy for accounting and financial requirements. Money is typically 2
decimal places but in some applications we need more accuracy.
