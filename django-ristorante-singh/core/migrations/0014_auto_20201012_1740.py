# Generated by Django 2.2.14 on 2020-10-12 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20201012_1622'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_id',
            new_name='code',
        ),
        migrations.AddField(
            model_name='payment',
            name='type_pay',
            field=models.BooleanField(default=False),
        ),
    ]
