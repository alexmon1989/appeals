# Generated by Django 3.2.12 on 2022-06-17 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0014_remove_document_appellant_reqs'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttemplate',
            options={'verbose_name': 'Шаблон документу', 'verbose_name_plural': 'Шаблони документів'},
        ),
    ]