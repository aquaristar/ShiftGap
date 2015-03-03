from django.conf.urls import patterns, include, url

from .views import TimeOffRequestListing

urlpatterns = \
    patterns('',
             url(r'^$', TimeOffRequestListing.as_view(), name='requests_home'),
             url(r'^submit_time_off_request/$', 'apps.availability.views.submit_time_off_request', name='post_request'),
             url(r'^cancel_time_off_request/$', 'apps.availability.views.cancel_time_off_request', name='post_cancel_request'),
             )