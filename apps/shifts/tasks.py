from __future__ import absolute_import

from django.conf import settings
from django.db import transaction

import arrow
from django_twilio.client import twilio_client

from shiftgap.celery import app
from .models import Shift


@app.task
def notify_employees_new_schedule_posted():
    pass


@app.task
def notify_imminent_shift_add():
    # if an employee is added to a shift that starts within the next
    pass


@app.task
def new_shift_reminder(shift_id):
    # if shift is NEW
    # and shift is published
    # and within 36 hours
    # we notify the user IMMEDIATELY
    # otherwise normal notifications will suffice
    shift = Shift.objects.get(pk=shift_id)
    if shift.user.userprofile.phone_reminders:
        if shift.user.userprofile.phone_number:
            start = shift.start_time.strftime('%l:%M%p on %b %d')  # ' 1:36PM on Oct 18'
            # Translators: This is a text message limited to 139 characters.
            message = "%s you've been added to a shift on %s" % shift.user.username, start
            phone = shift.user.userprofile.phone_number
            msg = twilio_client.messages.create(
                body=message,
                to=phone,
                from_=settings.TWILIO_DEFAULT_CALLERID
            )


@app.task
def twenty_four_hour_reminder():
    # Get all shifts
    next24 = arrow.utcnow().replace(hours=+24)
    shifts = Shift.objects.filter(start_time__lte=next24.datetime, start_time__gte=arrow.utcnow().datetime)
    # if the start time is < 24 hours away AND twenty_four_hour_reminder_sent is false
    for shift in shifts:
        # if a reminder hasn't already been sent
        if not shift.twenty_four_hour_reminder_sent and shift.published:
            # if a users phone reminders are enabled
            with transaction.atomic():
                if shift.user.userprofile.phone_reminders and shift.user.userprofile.phone_confirmed:
                    # send a reminder
                    user_start_time = shift.start_time.astimezone(shift.user.userprofile.timezone)
                    # user_start_time = arrow.get(user_start_time).humanize()
                    user_start_time = user_start_time.strftime('%l:%M%p on %b %d')  # ' 1:36PM on Oct 18'
                    # Translators: This is a text message limited to 139 characters.
                    message = "%s, you are scheduled to work %s" % (shift.user.first_name, user_start_time)
                    sms = twilio_client.messages.create(
                        body=message,
                        to=shift.user.userprofile.phone_number,
                        from_=settings.TWILIO_DEFAULT_CALLERID
                    )
                    shift.twenty_four_hour_reminder_sent = True
                    shift.save()


@app.task
def ninety_minute_reminder():
    # Get all shifts
    next90 = arrow.utcnow().replace(minutes=+95)
    shifts = Shift.objects.filter(start_time__lte=next90.datetime, start_time__gte=arrow.utcnow().datetime)
    # if the start time is < 95 minutes away AND ninety_minute_reminder_sent is false
    for shift in shifts:
        # if a reminder hasn't already been sent
        if not shift.ninety_minute_reminder_sent and shift.published:
            # if a users phone reminders are enabled
            with transaction.atomic():
                if shift.user.userprofile.phone_reminders and shift.user.userprofile.phone_confirmed:
                    # send a reminder
                    # make the time in the users own timezone
                    user_start_time = shift.start_time.astimezone(shift.user.userprofile.timezone)
                    # user_start_time = arrow.get(user_start_time).humanize()
                    user_start_time = user_start_time.strftime('%l:%M%p on %b %d')  # ' 1:36PM on Oct 18'
                    # Translators: This is a text message limited to 139 characters.
                    message = "%s, you have a shift starting soon %s." % (shift.user.first_name, user_start_time)
                    sms = twilio_client.messages.create(
                        body=message,
                        to=shift.user.userprofile.phone_number,
                        from_=settings.TWILIO_DEFAULT_CALLERID
                    )
                    shift.ninety_minute_reminder_sent = True
                    shift.save()