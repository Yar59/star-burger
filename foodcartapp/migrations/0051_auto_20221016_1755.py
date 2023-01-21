# Generated by Django 3.2.15 on 2022-10-16 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_orderdistancetorestaurant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdistancetorestaurant',
            name='order_coordinates',
        ),
        migrations.AddField(
            model_name='orderdistancetorestaurant',
            name='order_lat',
            field=models.FloatField(default=1, verbose_name='Координаты заказчика(Широта)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderdistancetorestaurant',
            name='order_lon',
            field=models.FloatField(default=1.0, verbose_name='Координаты заказчика(Долгота)'),
            preserve_default=False,
        ),
    ]
