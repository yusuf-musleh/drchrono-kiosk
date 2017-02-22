# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0004_auto_20170222_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='appointment_id',
            field=models.IntegerField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appointment',
            name='time_waited',
            field=models.DurationField(null=True),
        ),
    ]
