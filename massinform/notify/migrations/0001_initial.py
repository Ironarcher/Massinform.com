# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('listname', models.CharField(max_length=100)),
                ('firstnames', models.TextField(default=b'[]')),
                ('lastnames', models.TextField(default=b'[]')),
                ('phonenumbers', models.TextField(default=b'[]')),
                ('emailaddresses', models.TextField(default=b'[]')),
                ('recentnotifications', models.TextField(default=b'[]')),
                ('rnottimes', models.TextField(default=b'[]')),
            ],
        ),
    ]
