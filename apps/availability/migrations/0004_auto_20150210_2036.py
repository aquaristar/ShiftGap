# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0003_auto_20150209_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availability',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='availability',
            name='start_time',
        ),
    ]
