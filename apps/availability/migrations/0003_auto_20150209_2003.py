# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0002_auto_20150209_2001'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together=set([('start_date', 'user'), ('start_date', 'end_date', 'user'), ('end_date', 'user')]),
        ),
    ]
