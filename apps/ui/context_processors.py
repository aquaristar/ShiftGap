from os import environ
import datetime
import arrow

from django.utils import timezone


def process_ui_views(request):
    return {'build': environ.get('BUILD_HASH', None),
            'time': arrow.utcnow().datetime,
            'naive': timezone.is_aware(arrow.utcnow().datetime),
            'yourtz': request.session.get('django_timezone', None),
            }