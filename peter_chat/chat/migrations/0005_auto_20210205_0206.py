# Generated by Django 3.1.4 on 2021-02-05 02:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_chat_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='name',
            new_name='chatName',
        ),
    ]
