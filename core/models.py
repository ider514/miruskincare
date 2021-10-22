from django.db.models.expressions import F
from core.forms import DELIVERY
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
import uuid


DELIVERY_A = 4000
DELIVERY_B = 5500


CATEGORY_CHOICES = (
    ('CH', 'Чийгшүүлэгч тос'),
    ('TS', 'Цэвэрлэгч'),
    ('TO', 'Тонер'),
    ('NT', 'Нарны тос'),
    ('HE', 'Хөгшрөлтийн эсрэг'),
    ('GU', 'Гуужуулагч'),
    ('ES', 'Эссэнц'),
    ('SE', 'Серум'),
    ('UA', 'Үс арчилгаа'),
    ('BA', 'Бие арчилгаа'),
    ('MA', 'Маск'),
    ('NB', 'Нүүрний будаг'),
    ('ZT', 'Зовхины тос'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class Carousel(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField()
    description = models.TextField(blank=True)
    button = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    stock_amount = models.IntegerField(null=False)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    sold_out = models.BooleanField(default=False)
    special = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def order_item(self):
        self.stock_amount = self.stock_amount - 1
        self.save()


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    uuid = models.CharField(unique=True, max_length=6, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    delivery_fee = models.CharField(max_length=5, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    payment_received = models.BooleanField(default=False)
    contact = models.IntegerField(blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    address_detail = models.CharField(max_length=200)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def save(self, *args, **kwargs):
        if not self.pk:
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would
            # have pk
            self.uuid = uuid.uuid4().hex[:6].upper()
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def get_items(self):
        return self.items

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        if self.delivery_fee == "a":
            return total + DELIVERY_A
        elif self.delivery_fee == "b":
            return total + DELIVERY_B
        else:
            return total

    def get_delivery_fee(self):
        if self.delivery_fee == "a":
            return DELIVERY_A
        elif self.delivery_fee == "b":
            return DELIVERY_B
        else:
            return None


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    duureg = models.CharField(max_length=100)
    khoroo_khotkhon = models.CharField(max_length=100)
    bair = models.CharField(max_length=100)
    orts = models.CharField(max_length=100)
    davhar = models.CharField(max_length=100)
    toot = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    nemelt = models.CharField(max_length=150)

    def get_string(self):
        return (self.duureg + self.khoroo_khotkhon)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
