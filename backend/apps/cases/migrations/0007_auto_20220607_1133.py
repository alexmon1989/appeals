# Generated by Django 3.2.12 on 2022-06-07 08:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0007_claim'),
        ('cases', '0006_auto_20220520_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='claim',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='filling.claim', verbose_name='Звернення'),
        ),
        migrations.AlterModelTable(
            name='document',
            table='documents',
        ),
        migrations.AlterModelTable(
            name='sign',
            table='documents_signs',
        ),
    ]
