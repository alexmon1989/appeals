# Generated by Django 3.2.12 on 2022-05-30 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0005_alter_claimfield_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimfield',
            name='enabled',
            field=models.BooleanField(default=True, verbose_name='Включено'),
        ),
    ]