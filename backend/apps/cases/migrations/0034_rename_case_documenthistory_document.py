# Generated by Django 4.0.6 on 2022-09-28 23:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0033_documenthistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documenthistory',
            old_name='case',
            new_name='document',
        ),
    ]