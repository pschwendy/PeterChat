# Generated by Django 3.1.4 on 2021-02-05 02:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_auto_20210205_0206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='chatName',
            new_name='chat_name',
        ),
    ]
