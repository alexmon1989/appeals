# Generated by Django 4.0.6 on 2022-11-29 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0016_alter_claim_submission_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='internal_claim',
            field=models.BooleanField(default=False, verbose_name='Заявка створена у внутрішньому модулі'),
        ),
    ]