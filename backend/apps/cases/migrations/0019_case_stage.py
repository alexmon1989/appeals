# Generated by Django 4.0.6 on 2022-07-25 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0018_sign_file_signed'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='stage',
            field=models.IntegerField(choices=[(0, 'Нове звернення'), (1, 'Створення розпорядження про створення колегії'), (2, 'Прийняття до розгляду звернення'), (3, 'Розгляд звернення')], default=0, verbose_name='Стадія розгляду'),
        ),
    ]
