# Generated by Django 3.2.12 on 2022-06-17 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0013_auto_20220617_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='appellant_reqs',
        ),
    ]
