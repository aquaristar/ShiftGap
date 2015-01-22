from django.conf.urls import patterns, include, url

from .views import UserListView

urlpatterns = patterns('',

                       url(r'^members/$', UserListView.as_view(), name='user_list'),

                       )