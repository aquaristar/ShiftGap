# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together=set([('location', 'name')]),
        ),
    ]
