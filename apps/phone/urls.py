from django.conf.urls import patterns, include, url

from .views import ConfirmPhoneView

urlpatterns = \
    patterns('',

             # all incoming voice calls go to this endpoint
             url(r'^phone/$', 'apps.phone.views.greet_by_name', name='phone_test'),

             # all incoming sms messages to to this endpoint
             url(r'^sms/$', 'apps.phone.views.record_incoming_sms', name='record_incoming_sms'),

             url(r'^confirm/$', ConfirmPhoneView.as_view(), name='confirm_phone'),
             )