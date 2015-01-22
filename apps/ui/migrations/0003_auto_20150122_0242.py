# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0002_auto_20150120_0439'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_confirmed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default='USR', choices=[('USR', 'User'), ('MGR', 'Manager'), ('ADM', 'Administrator')], max_length=3),
            preserve_default=True,
        ),
    ]
