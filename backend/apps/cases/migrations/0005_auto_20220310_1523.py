# Generated by Django 3.2.12 on 2022-03-10 13:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0004_auto_20220310_1453'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collegiummembership',
            options={'verbose_name': 'Колегія', 'verbose_name_plural': 'Колегії'},
        ),
        migrations.AlterField(
            model_name='collegiummembership',
            name='is_head',
            field=models.BooleanField(default=False, verbose_name='Голова колегії'),
        ),
        migrations.AlterField(
            model_name='collegiummembership',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Користувач'),
        ),
        migrations.AlterModelTable(
            name='collegiummembership',
            table='cases_collegium_membership',
        ),
    ]
