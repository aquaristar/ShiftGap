from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from .views import ShiftListView, ShiftCreateView, ShiftUpdateView


urlpatterns = \
    patterns('',

             url(r'^$', ShiftListView.as_view(), name='shift_list'),
             url(r'^shift/edit/(?P<pk>\d+)/$', ShiftUpdateView.as_view(), name='shift_update'),
             url(r'^shift/', ShiftCreateView.as_view(), name='shift_create'),
             )