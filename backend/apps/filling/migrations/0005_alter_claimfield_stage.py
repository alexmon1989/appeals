# Generated by Django 3.2.12 on 2022-05-29 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filling', '0004_auto_20220526_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimfield',
            name='stage',
            field=models.PositiveIntegerField(choices=[(3, '3. Номер заявки/охоронного документа'), (4, "4. Дані об'єкта права інтелектуальної власності"), (5, '5. Відомості про заявника (апелянта) та власника'), (6, '6. Відомостей про апелянта (лише у випадку заперечень 3-х осіб і апеляційних заяв)'), (7, '7. Додаткова інформація'), (8, '8. Відомості щодо рішення Укрпатенту'), (9, '9. Додатки (файли)')], verbose_name='Етап вводу на формі'),
        ),
    ]