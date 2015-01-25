from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from apps.organizations.models import Organization

from timezone_field import TimeZoneField


class UserProfile(models.Model):
    USER = 'USR'
    MANAGER = 'MGR'
    ADMINISTRATOR = 'ADM'
    USER_ROLES = (
        (USER, _('User')),
        (MANAGER, _('Manager')),
        (ADMINISTRATOR, _('Administrator'))
    )

    user = models.OneToOneField('auth.User')
    organization = models.ForeignKey(Organization)
    timezone = TimeZoneField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(max_length=15, blank=True, validators=[phone_regex],
                                    verbose_name=_('Full number including country code and +'))
    phone_confirmation_code = models.CharField(max_length=5, blank=True)
    phone_reminders = models.BooleanField(default=True)
    phone_confirmed = models.BooleanField(default=False)
    role = models.CharField(max_length=3, choices=USER_ROLES, default=USER)

    __original_number = None

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_number = self.phone_number

    def __str__(self):
        return _('Profile for ') + self.user.username

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # if a user changes their phone number, we need to make them confirm it again
        if self.phone_number != self.__original_number:
            self.phone_confirmed = False
            self.phone_confirmation_code = ''
        super(UserProfile, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                      update_fields=update_fields)
        self.__original_number = self.phone_number

    @property
    def admin(self):
        return True if self.role == 'ADM' else False

    @property
    def manager(self):
        return True if self.role == 'MGR' else False

    @property
    def admin_or_manager(self):
        return True if self.role == 'ADM' or self.role == 'MGR' else False