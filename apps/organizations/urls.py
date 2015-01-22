from django.conf.urls import patterns, include, url

from .views import UserListView, UserSetupView

urlpatterns = patterns('',

                       url(r'^members/new/$', UserSetupView.as_view(), name='user_setup'),
                       url(r'^members/$', UserListView.as_view(), name='user_list'),
                       )