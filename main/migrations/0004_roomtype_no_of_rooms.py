# Generated by Django 3.0.3 on 2020-03-27 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20200322_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomtype',
            name='No_of_Rooms',
            field=models.PositiveSmallIntegerField(default=True),
        ),
    ]
