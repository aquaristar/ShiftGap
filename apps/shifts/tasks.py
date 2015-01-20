from __future__ import absolute_import

from django.conf import settings

from django_twilio.client import twilio_client

from shiftgap.celery import app
from .models import Shift


@app.task
def echo():
    print('Hello world....')


@app.task
def new_shift_reminder(shift_id):
    shift = Shift.objects.get(pk=shift_id)
    if shift.user.userprofile.phone_reminders:
        if shift.user.userprofile.phone:
            # send a txt message
            message = "%s you've been added to a shift." % shift.user.username
            phone = shift.user.userprofile.phone
            print(message)
            print(phone)
            msg = twilio_client.messages.create(
                body=message,
                to=phone,
                from_=settings.TWILIO_DEFAULT_CALLERID
            )