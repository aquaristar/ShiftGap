# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0003_auto_20150122_0242'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='phone',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_confirmation_code',
            field=models.CharField(blank=True, max_length=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=25, verbose_name='Full number including country code, +1'),
            preserve_default=True,
        ),
    ]
