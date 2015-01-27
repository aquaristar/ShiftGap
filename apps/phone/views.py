from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import arrow
from twilio import twiml
from django_twilio.decorators import twilio_view

from apps.organizations.views import UserProfileRequiredMixin
from apps.shifts.models import Shift
from apps.ui.models import UserProfile


def process(request):
    print(request.GET)
    return HttpResponse()

@twilio_view
def greet_by_name(request):
    r = twiml.Response()
    from shiftgap.celery import debug_task
    debug_task.delay()
    from apps.shifts.tasks import echo
    echo.delay()
    if request.POST['From'] == '+15876740115':
        r.say('Buenos dias miguel', voice='Male', language='es', loop=None)
    elif request.POST['From'] == '+17803817007':
        r.say('Bonjour michael, je croix que vous allex avoir beaucoup de fun avec Twilio', voice='Female', language='fr', loop=None)
    else:
        r.say('Sorry you number is not identified with our system, please enter your personal access code.',
              voice='Female', language='en', loop=None)
    return r


@twilio_view
def record_incoming_sms(request):

    r = twiml.Response()
    message = request.POST['Body'].lower()
    if message == 'stop' or message == 'unsubscribe':
        '''
        Stop and un subscribe messages are handled at the Twilio level but they pass the information along
        to us so that we can update our records accordingly. No responses will be made when to the STOP or
        un subscribe message.
        See: https://www.twilio.com/help/faq/sms/does-twilio-support-stop-block-and-cancel-aka-sms-filtering
        '''
        ups = UserProfile.objects.filter(phone_number=request.POST['From'])
        for up in ups:
            up.phone_confirmed = False
            up.save()
    if message == 'start' or message == 'yes':
        # Responses will be sent to the START and YES messages
        ups = UserProfile.objects.filter(phone_number=request.POST['From'])
        for up in ups:
            up.phone_confirmed = True
            up.save()
        if ups:
            name = ups[0].user.first_name
            msg = _('Hi %s, your number is now confirmed!') % name
            r.message(msg=msg)

    if message == 'next':
        now = arrow.utcnow().datetime
        shifts = Shift.objects.filter(user__userprofile__phone_number=request.POST['From'],
                                      start_time__gte=now).order_by('start_time')
        if shifts:
            start = shifts[0].start_time.strftime('%l:%M%p on %b %d')  # ' 1:36PM on Oct 18'
            msg = _('Your next shift is at %s') % start
            r.message(msg=msg)
    return r


class ConfirmPhoneView(UserProfileRequiredMixin, TemplateView):
    template_name = 'phone/phone_confirm.html'

    def post(self, request, *args, **kwargs):
        # if user has no confirmation code, tell them
        if not request.user.userprofile.phone_confirmation_code:
            messages.warning(request, _('It looks like you haven\'t sent a confirmation to your phone yet.'))
            return HttpResponseRedirect(reverse('home'))

        if request.POST['confirmation'] == '' or len(request.POST['confirmation']) < 5:
            messages.error(request, _('Invalid confirmation code entered, please try again.'))
            return HttpResponseRedirect(reverse('phone:confirm_phone'))
        else:
            if request.POST['confirmation'] == request.user.userprofile.phone_confirmation_code:
                request.user.userprofile.phone_confirmed = True
                request.user.userprofile.save()
                messages.success(request, _('Your phone number is now verified!'))
                return HttpResponseRedirect(reverse('home'))