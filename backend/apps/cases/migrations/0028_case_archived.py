# Generated by Django 4.0.6 on 2022-08-01 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0027_casestagestep_case_stopped'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Передано в архів'),
        ),
    ]
