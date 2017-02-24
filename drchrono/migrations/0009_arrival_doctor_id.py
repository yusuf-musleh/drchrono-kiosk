# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0008_arrival'),
    ]

    operations = [
        migrations.AddField(
            model_name='arrival',
            name='doctor_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
