from django.conf.urls import patterns, include, url

urlpatterns = \
    patterns('',

             # all incoming voice calls go to this endpoint
             url(r'^phone/$', 'apps.phone.views.greet_by_name', name='phone_test'),

             # all incoming sms messages to to this endpoint
             url(r'^sms/$', 'django_twilio.views.message', {
                 'message': 'Thanks for the message. A representative will get back to you shortly.'
             }),
             )