from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from .views import ShiftListView, ShiftCreateView, ShiftUpdateView, ShiftListCalendarView, ShiftListForUserView, \
    ShiftPublishFormView, ShiftUnpublishFormView


urlpatterns = \
    patterns('',

             url(r'^$', ShiftListView.as_view(), name='shift_list'),
             url(r'^me/$', ShiftListForUserView.as_view(), name='shift_list_user'),
             url(r'^publish/$', ShiftPublishFormView.as_view(), name='shift_publish_range'),
             url(r'^unpublish/$', ShiftUnpublishFormView.as_view(), name='shift_unpublish_range'),
             # FIXME edit view doesn't load initial data
             url(r'^shift/edit/(?P<pk>\d+)/$', ShiftUpdateView.as_view(), name='shift_update'),
             url(r'^calendar/delete/$', 'apps.shifts.views.delete_shift_from_calendar', name='shift_delete_calendar'),
             url(r'^calendar/$', ShiftListCalendarView.as_view(), name='shift_calendar'),
             url(r'^shift/', ShiftCreateView.as_view(), name='shift_create'),

             # Testing view do not use in production
             # url(r'^worker/$', 'apps.shifts.views.spawn_worker'),
             # url(r'^stream/$', 'apps.shifts.views.stream_response'),
    )