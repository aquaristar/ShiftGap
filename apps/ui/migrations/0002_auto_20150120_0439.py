# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=25),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_reminders',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
