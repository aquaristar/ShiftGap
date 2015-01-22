from django.conf.urls import patterns, url

from .views import UserListView, UserSetupView, JoinExistingOrganizationView

urlpatterns = patterns('',

                       url(r'^existing/$', JoinExistingOrganizationView.as_view(), name='join_existing'),
                       url(r'^members/new/$', UserSetupView.as_view(), name='user_setup'),
                       url(r'^members/$', UserListView.as_view(), name='user_list'),
                       )