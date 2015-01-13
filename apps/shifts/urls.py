from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from .views import ShiftListView, ShiftCreateView, ShiftUpdateView, ShiftListCalendarView, ShiftListCreateUpdateAPIView


urlpatterns = \
    patterns('',

             url(r'^$', ShiftListView.as_view(), name='shift_list'),
             url(r'^shift/edit/(?P<pk>\d+)/$', ShiftUpdateView.as_view(), name='shift_update'),
             url(r'^calendar/$', ShiftListCalendarView.as_view(), name='shift_calendar'),
             url(r'^shift/', ShiftCreateView.as_view(), name='shift_create'),

             # FIXME give api endpoints their own urls not under /shifts/
             url(r'^api/shifts/$', ShiftListCreateUpdateAPIView.as_view(), name='shift_list_create_api'),
             )