from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from .views import ShiftListView, ShiftCreateView, ShiftUpdateView, ShiftListCalendarView, ShiftListCreateUpdateAPIView,\
    ShiftDeleteAPIView, ShiftDeleteView


urlpatterns = \
    patterns('',

             url(r'^$', ShiftListView.as_view(), name='shift_list'),
             url(r'^shift/edit/(?P<pk>\d+)/$', ShiftUpdateView.as_view(), name='shift_update'),
             url(r'^shift/delete/$', ShiftDeleteView.as_view(), name='shift_delete'),
             url(r'^calendar/delete/$', 'apps.shifts.views.delete_shift_from_calendar', name='shift_delete_calendar'),
             url(r'^calendar/$', ShiftListCalendarView.as_view(), name='shift_calendar'),
             url(r'^shift/', ShiftCreateView.as_view(), name='shift_create'),

             # FIXME give api endpoints their own urls not under /shifts/
             url(r'^api/shifts/$', ShiftListCreateUpdateAPIView.as_view(), name='shift_list_create_api'),
             )