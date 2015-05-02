from django.conf.urls import patterns, url

from .views import UserListView, UserSetupView, JoinExistingOrganizationView, UserEditView, NonActiveUserListView, \
    DeactivateUserView, ReactivateUserView

urlpatterns = patterns('',

                       url(r'^existing/$', JoinExistingOrganizationView.as_view(), name='join_existing'),
                       url(r'^members/new/$', UserSetupView.as_view(), name='user_setup'),
                       url(r'^members/deactivate/(?P<pk>\d+)/$', DeactivateUserView.as_view(), name='user_deactivate'),
                       url(r'^members/reactivate/(?P<pk>\d+)/$', ReactivateUserView.as_view(), name='user_reactivate'),
                       url(r'^members/(?P<pk>\d+)/edit/$', UserEditView.as_view(), name='user_edit'),
                       url(r'^members/non-active/$', NonActiveUserListView.as_view(), name='user_list_non_active'),
                       url(r'^members/$', UserListView.as_view(), name='user_list'),
                       )