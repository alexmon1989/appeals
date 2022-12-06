# Generated by Django 4.0.6 on 2022-12-06 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classifiers', '0023_objkind_cead_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommandType',
            fields=[
                ('id', models.AutoField(db_column='id_type_comm', primary_key=True, serialize=False)),
                ('command_name', models.CharField(blank=True, max_length=100, null=True)),
                ('who_run', models.CharField(blank=True, max_length=50, null=True)),
                ('command_comment', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'db_table': 'cl_commands_list',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='objkind',
            name='abbr',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Абревіатура'),
        ),
    ]
