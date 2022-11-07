# Generated by Django 4.0.6 on 2022-10-26 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_paymentcase_remove_payment_approved_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentcase',
            options={'verbose_name': 'Справа', 'verbose_name_plural': 'Справи'},
        ),
        migrations.AddField(
            model_name='payment',
            name='value',
            field=models.FloatField(default=0, verbose_name='Сума'),
            preserve_default=False,
        ),
    ]