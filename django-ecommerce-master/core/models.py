from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save

from utente.models import *
from django.shortcuts import reverse

# User = get_user_model()


CATEGORY_CHOICES = (
    ('S', 'Secondo'),
    ('F', 'Primo'),
    ('C', 'Contorno'),
    ('A', 'Antipasto'),
    ('D', 'Dolce'),
    ('P', 'PIZZA'),
    ('B', 'BEVANDE'),

)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
)

ADDRESS_CHOICES = (
    ('S', 'Shipping'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

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


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    cap = models.CharField(max_length=5)
    città = models.CharField(max_length=50)
    via = models.CharField(max_length=50)
    n_civico = models.CharField(max_length=10)
    piano = models.CharField(max_length=30, blank=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name_plural = 'Addresses'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,
                                         blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


""" billing_address = models.ForeignKey(
     'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
     coupon = models.ForeignKey(
    'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
 """

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




class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = User.objects.create(user=instance)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    chair = models.IntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)])
    date_start = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address=models.ManyToManyField(Address)
    booking=models.ManyToManyField(Booking)
    def __str__(self):
        return f'Profilo di {self.user.first_name} {self.user.last_name}'



class Gallery(models.Model):
    photo_path = models.ImageField(upload_to='gallery')

    def __str__(self):
        immagine = str(self.photo_path)
        return immagine

    class Meta:
        verbose_name_plural = 'ImmaginiGallery'
