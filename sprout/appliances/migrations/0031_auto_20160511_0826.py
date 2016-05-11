# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-11 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appliances', '0030_bugquery'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliance',
            name='ssh_failed',
            field=models.BooleanField(
                default=False, help_text=b'If last swap check failed on SSH.'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='swap',
            field=models.IntegerField(
                blank=True, help_text=b'How many MB is the appliance in swap.', null=True),
        ),
    ]
