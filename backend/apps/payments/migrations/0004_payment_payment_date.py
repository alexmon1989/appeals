# Generated by Django 4.0.6 on 2022-10-26 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_alter_paymentcase_options_payment_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(default='2022-10-26', verbose_name='Дата оплати'),
            preserve_default=False,
        ),
    ]