# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0002_patient_patient_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='gender',
            field=models.CharField(default=b'O', max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')]),
        ),
    ]
