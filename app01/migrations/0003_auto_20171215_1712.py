# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-15 09:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_auto_20171215_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.EmailField(max_length=32, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='pwd',
            field=models.CharField(max_length=32, verbose_name='密码'),
        ),
    ]