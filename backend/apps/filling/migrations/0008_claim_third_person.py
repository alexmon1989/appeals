# Generated by Django 3.2.12 on 2022-06-08 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0007_claim'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='third_person',
            field=models.BooleanField(default=False, verbose_name='Апелянт - третя особа'),
        ),
    ]
