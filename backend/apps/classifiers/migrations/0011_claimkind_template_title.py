# Generated by Django 3.2.12 on 2022-06-21 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classifiers', '0010_documenttype_create_with_claim'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimkind',
            name='template_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Назва для шаблону MS Word'),
        ),
    ]
