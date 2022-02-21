# Generated by Django 3.2.12 on 2022-02-09 11:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classifiers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Номер справи')),
                ('app_number', models.CharField(max_length=255, verbose_name='Номер заявки (охоронного документа)')),
                ('obj_title', models.CharField(max_length=255, verbose_name="Назва об'єкта")),
                ('applicant_name', models.CharField(max_length=255, verbose_name='Найменування апелянта (заявника)')),
                ('applicant_represent', models.CharField(blank=True, max_length=255, verbose_name='Найменування представника апелянта')),
                ('mailing_address', models.CharField(blank=True, max_length=255, verbose_name='Адреса для листування')),
                ('claim_date', models.DateField(blank=True, null=True, verbose_name='Дата подання заперечення (заяви)')),
                ('deadline', models.DateField(blank=True, null=True, verbose_name='Дата, до якої необхідно розглянути заперечення')),
                ('hearing', models.DateField(blank=True, null=True, verbose_name='Дата призначенного засідання')),
                ('claim_kind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='classifiers.claimkind', verbose_name='Вид заяви/заперечення')),
                ('collegium', models.ManyToManyField(related_name='collegium', to=settings.AUTH_USER_MODEL, verbose_name='Члени колегії')),
                ('expert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expert', to=settings.AUTH_USER_MODEL, verbose_name='Вид заяви/заперечення')),
                ('obj_kind', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='classifiers.objkind', verbose_name="Вид об'єкта промислової власності")),
                ('papers_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='papers_owner', to=settings.AUTH_USER_MODEL, verbose_name='Особа, у якої знаходиться паперова справа')),
                ('secretary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secretary', to=settings.AUTH_USER_MODEL, verbose_name='Секретар')),
            ],
            options={
                'verbose_name': 'Справа',
                'verbose_name_plural': 'Справи',
                'db_table': 'cases_cases_list',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('registration_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Реєстраційний номер')),
                ('registration_date', models.DateField(blank=True, null=True, verbose_name='Дата реєстрації')),
                ('output_date', models.DateField(blank=True, null=True, verbose_name='Дата відправлення')),
                ('input_date', models.DateField(blank=True, null=True, verbose_name='Дата отримання')),
                ('case', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cases.case', verbose_name='Справа')),
                ('document_name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='classifiers.documentname', verbose_name='Назва документа')),
                ('document_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='classifiers.documenttype', verbose_name='Тип документа')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документи',
                'db_table': 'cases_documents_list',
            },
        ),
    ]
