from django.contrib import admin

from .models import Carousel, Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


# @admin.action(description='Payment received')
# def payment_received(modeladmin, request, queryset):
#     queryset.update(payment_received=True)

def payment_received(modeladmin, request, queryset):
    queryset.update(payment_received=True)


class OrderAdmin(admin.ModelAdmin):
    actions = [payment_received]
    list_display = ['user',
                    'ordered',
                    'payment_received',
                    'ordered_date',
                    # 'received',
                    # 'refund_requested',
                    # 'refund_granted',
                    # 'shipping_address',
                    # 'shipping_address_detail',
                    # 'coupon',
                    'delivery_fee',
                    'get_total',
                    'uuid'
                    ]
    list_display_links = [
        'user',
        # 'shipping_address',
        # 'billing_address',
        # 'payment',
        # 'coupon'
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


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title',
                    'stock_amount'
                    ]


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


admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Carousel)
