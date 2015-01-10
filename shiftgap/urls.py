##### Comment out if using i18n ####
from django.conf.urls import patterns, include, url
##### Uncomment if using i18n ####
# from django.conf.urls import include, url
# from django.conf.urls.i18n import patterns
from django.conf import settings
from django.contrib import admin

from django.views.generic import TemplateView, RedirectView
from django.http import HttpResponseRedirect

from apps.organizations.views import AccountProfileView

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='welcome.html'), name='home'),

    # include your apps urls files below

    # django all auth
    url(r'^login/$', RedirectView.as_view(url='/accounts/login/'),
        name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/login/'}, name='logout'),
    url(r'^accounts/profile/', AccountProfileView.as_view(), name='account_profile'),
    url(r'^accounts/', include('allauth.urls')),

    # Misc non django
    url(r'^404\.html$', TemplateView.as_view(template_name='404.html'), name='404'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain')),
    url(r'^crossdomain\.xml$', TemplateView.as_view(template_name='crossdomain.xml', content_type='text/xml')),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')), #google chrome favicon fix
)