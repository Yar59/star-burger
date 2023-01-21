# Generated by Django 3.2.15 on 2022-10-03 17:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['ordered_at'], 'verbose_name': 'заказ', 'verbose_name_plural': 'заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='ordered_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время заказа'),
        ),
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='order', to='foodcartapp.Product', verbose_name='Продукты'),
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='количество')),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена товара')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.order', verbose_name='заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='selected_product', to='foodcartapp.product', verbose_name='продукт')),
            ],
            options={
                'verbose_name': 'продукт заказа',
                'verbose_name_plural': 'продукты заказа',
                'ordering': ['id'],
            },
        ),
    ]
