# Generated by Django 3.2.15 on 2022-10-09 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20221009_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличными'), ('card', 'Картой'), ('unknown', 'Неизвестно')], db_index=True, default='unknown', max_length=12, verbose_name='Способ оплаты'),
        ),
    ]
