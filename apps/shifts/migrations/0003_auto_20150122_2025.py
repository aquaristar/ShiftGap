# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0002_auto_20150119_0341'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='ninety_minute_reminder_sent',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shift',
            name='published',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shift',
            name='twenty_four_hour_reminder_sent',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shift',
            name='user_has_confirmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
