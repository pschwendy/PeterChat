# Generated by Django 3.1.4 on 2021-01-16 22:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20201227_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateField(default=datetime.date(2020, 12, 10)),
        ),
    ]
