# Generated by Django 3.2.12 on 2022-05-26 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0003_auto_20220522_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimfield',
            name='stage',
            field=models.PositiveIntegerField(choices=[(3, "3. Дані об'єкта права інтелектуальної власності"), (4, '4. Відомості про заявника (апелянта) та власника'), (5, '5. Відомостей про апелянта (лише у випадку заперечень 3-х осіб і апеляційних заяв)'), (6, '6. Додаткова інформація'), (7, '7. Відомості щодо рішення Укрпатенту'), (8, '8. Додатки (файли)')], verbose_name='Етап вводу на формі'),
        ),
        migrations.AlterField(
            model_name='claimfield',
            name='title',
            field=models.CharField(max_length=1024, verbose_name='Назва'),
        ),
    ]