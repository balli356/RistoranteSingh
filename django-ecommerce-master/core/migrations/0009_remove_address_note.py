# Generated by Django 2.2.14 on 2020-09-25 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200925_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='note',
        ),
    ]