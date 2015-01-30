##### Comment out if using i18n ####
from django.conf.urls import patterns, include, url
##### Uncomment if using i18n ####
# from django.conf.urls import include, url
# from django.conf.urls.i18n import patterns
from django.conf import settings
from django.contrib import admin

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from apps.organizations.views import AccountProfileView, AccountProfileUpdateView, PostLoginView
from apps.shifts.views import ShiftListCreateUpdateAPIView, ShiftListFilteredAPIView, ShiftListUnpublishedAPIView,\
    ShiftUpdateAPIView

urlpatterns = patterns('',

    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='welcome.html'), name='home'),

    # include your apps urls files below
    url(r'^shifts/', include('apps.shifts.urls', namespace='shifts')),
    url(r'^organization/', include('apps.organizations.urls', namespace='org')),

    # redirects user after login if they have setup their org or not
    url(r'^postlogin/$', PostLoginView.as_view(), name='post_login'),

    # django all auth
    url(r'^login/$', RedirectView.as_view(url='/accounts/login/'),
        name='login'),
    url(r'^profile/update/', AccountProfileUpdateView.as_view(), name='account_profile_update'),
    url(r'^profile/$', RedirectView.as_view(url='/accounts/profile/')),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/login/'}, name='logout'),
    url(r'^accounts/profile/', AccountProfileView.as_view(), name='account_profile'),
    url(r'^accounts/', include('allauth.urls')),

    # user interaction with 'phone' app at /phone/, api interaction at /api/v1/t/
    url(r'^phone/', include('apps.phone.urls', namespace='phone'), name='phone'),
    # v1 telephony endpoints with twilio
    url(r'^api/v1/t/', include('apps.phone.urls', namespace='phone'), name='twilio'),
    # v1 api
    url(r'^api/v1/shifts/unpublished/$', ShiftListUnpublishedAPIView.as_view(), name='shift_list_unpublished_api'),
    url(r'^api/v1/shifts/filtered/$', ShiftListFilteredAPIView.as_view(), name='shift_list_filtered_api'),
    url(r'^api/v1/shifts/(?P<pk>\d+)/$', ShiftUpdateAPIView.as_view(), name='shift_update_api'),
    url(r'^api/v1/shifts/$', ShiftListCreateUpdateAPIView.as_view(), name='shift_list_create_api'),





    # Misc non django
    url(r'^404\.html$', TemplateView.as_view(template_name='404.html'), name='404'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),
    url(r'^crossdomain\.xml$', TemplateView.as_view(template_name='crossdomain.xml', content_type='text/xml')),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')), #google chrome favicon fix
)