# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanage', '0011_auto_20150812_0222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='liked_projects',
            new_name='contact_list_ids',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='about_me',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='country',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='fav_language',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='joined_on',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='recently_viewed_projects',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='showemail',
        ),
    ]
