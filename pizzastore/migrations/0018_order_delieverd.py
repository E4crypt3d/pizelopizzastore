# Generated by Django 4.0 on 2022-11-13 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pizzastore', '0017_rename_bakng_time_pizza_baking_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delieverd',
            field=models.BooleanField(default=False),
        ),
    ]
