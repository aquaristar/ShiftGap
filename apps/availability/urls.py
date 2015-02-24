from django.conf.urls import patterns, include, url

from .views import TimeOffRequestListingForUser

urlpatterns = \
    patterns('',
             url(r'^$', TimeOffRequestListingForUser.as_view(), name='requests_home'),
             )