# Generated by Django 4.0.6 on 2022-11-22 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classifiers', '0022_remove_decisiontype_obj_kind_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='objkind',
            name='cead_id',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Id у CEAD'),
        ),
    ]
