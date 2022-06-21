# Generated by Django 3.2.12 on 2022-06-17 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classifiers', '0008_auto_20220617_1212'),
        ('cases', '0012_documenttemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttemplate',
            name='documents_types',
            field=models.ManyToManyField(blank=True, to='classifiers.DocumentType', verbose_name='Типи документів'),
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='title',
            field=models.CharField(max_length=512, verbose_name='Назва шаблону'),
        ),
    ]
