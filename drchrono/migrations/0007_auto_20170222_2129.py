# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0006_auto_20170222_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='arrival_time',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
