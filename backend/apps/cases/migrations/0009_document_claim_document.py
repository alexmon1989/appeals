# Generated by Django 3.2.12 on 2022-06-13 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0008_document_auto_generated'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='claim_document',
            field=models.BooleanField(default=False, verbose_name='Подано або сформовано під час подання звернненя'),
        ),
    ]
