from django.contrib import admin

from .models import Item, OrderItem, Order, Payment,  Address,Gallery,Booking,Profile
from utente.models import *


# Register your models here.
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from utente.forms import UserAdminCreationForm, UserAdminChangeForm
from .models import User


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'shipping_address',
                    'payment',

                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'payment'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received'
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


"""class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']
"""

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Gallery)
admin.site.register(Booking)
admin.site.register(Address)
admin.site.register(Profile)

