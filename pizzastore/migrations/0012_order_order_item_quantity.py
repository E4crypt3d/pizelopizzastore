# Generated by Django 4.0 on 2022-11-09 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pizzastore', '0011_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_item_quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
