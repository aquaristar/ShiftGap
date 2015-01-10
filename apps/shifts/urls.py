from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from .views import ShiftListView


urlpatterns = patterns('',

                       url(r'^$', ShiftListView.as_view(), name='shift_list'),

)