from django.contrib import admin

from .models import Carousel, Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'payment_received',
                    'being_delivered',
                    'received',
                    # 'refund_requested',
                    # 'refund_granted',
                    'shipping_address',
                    'coupon',
                    'delivery_fee',
                    'get_total'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        # 'billing_address',
        # 'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   #    'refund_requested',
                   #    'refund_granted'
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    # actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'duureg',
        'khoroo_khotkhon',
        'bair',
        'orts',
        'davhar',
        'toot',
        'code',
        'nemelt',
    ]
    # list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'duureg', 'khoroo_khotkhon']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Carousel)
