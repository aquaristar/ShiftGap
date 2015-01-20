from django.http import HttpResponse

from twilio import twiml
from django_twilio.decorators import twilio_view


def process(request):
    print(request.GET)
    return HttpResponse()

@twilio_view
def greet_by_name(request):
    r = twiml.Response()
    if request.POST['From'] == '+15876740115':
        r.say('Buenos dias miguel', voice='Male', language='es', loop=None)
    elif request.POST['From'] == '+17803817007':
        r.say('Bonjour michael, je croix que vous allex avoir beaucoup de fun avec Twilio', voice='Female', language='fr', loop=None)
    else:
        r.say('Sorry you number is not identified with our system, please enter your personal access code.',
              voice='Female', language='en', loop=None)
    return r