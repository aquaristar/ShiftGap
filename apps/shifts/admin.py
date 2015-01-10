from django.contrib import admin

from .models import Shift, Schedule

# Register your models here.
admin.site.register(Shift)
admin.site.register(Schedule)