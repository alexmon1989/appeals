# Generated by Django 4.0.6 on 2022-08-26 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0031_case_refusal_reasons'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DocumentTemplate',
        ),
    ]