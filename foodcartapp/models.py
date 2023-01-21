from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Sum, F


class Place(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=200,
        db_index=True,
    )
    lat = models.FloatField(
        'Широта'
    )
    lon = models.FloatField(
        'Долгота'
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    lat = models.FloatField(
        'Широта',
        default=0
    )
    lon = models.FloatField(
        'Долгота',
        default=0
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def calculate_order_cost(self):
        return self.annotate(
            order_cost=Sum(
                F('order_products__price') * F('order_products__quantity')
            )
        )


class Order(models.Model):
    HANDLED_ORDER = 'handled'
    NEW_ORDER = 'unhandled'
    IN_WORK = 'in_work'
    STATUS = [
        (HANDLED_ORDER, 'Обработанный'),
        (NEW_ORDER, 'Необработанный'),
        (IN_WORK, 'В работе')
    ]
    CASH = 'cash'
    CARD = 'card'
    UNKNOWN = 'unknown'
    PAYMENT_METHOD = [
        (CASH, 'Наличными'),
        (CARD, 'Картой'),
        (UNKNOWN, 'Неизвестно')
    ]
    order_status = models.CharField(
        'Статус заказа',
        max_length=20,
        choices=STATUS,
        default=NEW_ORDER,
        db_index=True,
    )
    payment_method = models.CharField(
        'Способ оплаты',
        choices=PAYMENT_METHOD,
        default=UNKNOWN,
        max_length=12,
        db_index=True
    )
    firstname = models.CharField(
        'Имя',
        max_length=30,
        db_index=True,
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=30,
        db_index=True,
        blank=True,
    )
    address = models.CharField(
        'Адрес заказчика',
        max_length=200,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        'Номер телефона',
        db_index=True,
    )
    ordered_at = models.DateTimeField(
        'Время заказа',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Позвонили в',
        blank=True,
        null=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'Доставлен в',
        blank=True,
        null=True,
        db_index=True
    )
    comment = models.TextField(
        'Комментарий к заказу',
        blank=True,
    )
    cooking_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='Ресторан в котором будут готовить',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    place = models.ForeignKey(
        Place,
        related_name='orders',
        verbose_name='Место на карте',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['ordered_at', ]

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='order_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        verbose_name='продукт',
        related_name='order_products'
    )
    quantity = models.PositiveIntegerField(
        'количество',
        default=1,
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f'{self.order} {self.product}'

    class Meta:
        ordering = ['id', ]
        verbose_name = 'продукт заказа'
        verbose_name_plural = 'продукты заказа'
