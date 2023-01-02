# Generated by Django 4.0.6 on 2022-12-29 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classifiers', '0029_stopreason'),
        ('cases', '0046_remove_case_hearing_case_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='stop_reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='classifiers.stopreason', verbose_name='Причина припинення розгляду справи'),
        ),
    ]