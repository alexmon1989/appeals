# Generated by Django 4.0.6 on 2022-07-25 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0013_remove_claimfield_base_doc'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='obj_title',
            field=models.CharField(default='', max_length=1024, verbose_name='Назва ОПІВ'),
            preserve_default=False,
        ),
    ]
