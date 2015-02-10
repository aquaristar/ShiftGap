# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('availability', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together=set([('end_date', 'user'), ('start_date', 'user')]),
        ),
    ]
