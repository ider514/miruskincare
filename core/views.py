import random
import string
import uuid

# import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import NON_FIELD_ERRORS, ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Carousel

# stripe.api_key = settings.STRIPE_SECRET_KEY

from django.core.mail import send_mail


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['carousel'] = Carousel.objects.all()
        context['item'] = Item.objects.all()
        context['special'] = Item.objects.all().filter(special=True)
        # And so on for more models
        return context


class SaleView(ListView):
    model = Item
    paginate_by = 10
    template_name = "sale.html"

    def get_context_data(self, **kwargs):
        context = super(SaleView, self).get_context_data(**kwargs)
        sale_items = list(Item.objects.all())

        sale_items[:] = [x for x in sale_items if x.discount_price is not None]
        context['item'] = sale_items
        return context


class NewView(ListView):
    model = Item
    paginate_by = 10
    template_name = "new.html"

    def get_context_data(self, **kwargs):
        context = super(NewView, self).get_context_data(**kwargs)
        sale_items = list(Item.objects.all())

        # sale_items[:] = [x for x in sale_items if x.discount_price is not None]
        context['item'] = sale_items
        return context


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Танд идэвхтэй захиалга байхгүй байна")
            return redirect("core:order-summary")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(form.errors)
            if form.is_valid():
                # use_default_shipping = form.cleaned_data.get(
                #     'use_default_shipping')
                # if use_default_shipping:
                #     print("Using the defualt shipping address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='S',
                #         default=True
                #     )
                #     if address_qs.exists():
                #         shipping_address = address_qs[0]
                #         order.shipping_address = shipping_address
                #         order.save()
                #     else:
                #         messages.info(
                #             self.request, "No default shipping address available")
                #         return redirect('core:checkout')
                # else:
                duureg = form.cleaned_data.get(
                    'duureg')
                khoroo_khotkhon = form.cleaned_data.get(
                    'khoroo_khotkhon')
                bair = form.cleaned_data.get(
                    'bair')
                orts = form.cleaned_data.get(
                    'orts')
                davhar = form.cleaned_data.get(
                    'davhar')
                toot = form.cleaned_data.get(
                    'toot')
                code = form.cleaned_data.get(
                    'code')
                nemelt = form.cleaned_data.get(
                    'nemelt')
                contact = form.cleaned_data.get(
                    'contact')
                delivery = form.cleaned_data.get(
                    'delivery')
                address_detail = ''
                address_detail = duureg[0] + ' дүүрэг, ' + \
                    khoroo_khotkhon + ' Хороо / Хотхон, ' + bair + ' Байр, ' + \
                    orts + ' Орц, ' + davhar + ' Давхар, ' + toot + ' Тоот, Орцны код: ' + \
                    code + ' Нэмэлт: ' + nemelt + ' дугаар: ' + contact
                if is_valid_form([duureg, khoroo_khotkhon, bair, orts, davhar, toot, contact]):
                    shipping_address = Address(
                        user=self.request.user,
                        duureg=duureg,
                        khoroo_khotkhon=khoroo_khotkhon,
                        bair=bair,
                        orts=orts,
                        davhar=davhar,
                        toot=toot,
                        code=code,
                        nemelt=nemelt,
                    )
                    shipping_address.save()

                    order.shipping_address = shipping_address
                    order.contact = contact
                    order.delivery_fee = delivery
                    order.ordered = True
                    order.address_detail = address_detail
                    order.save()
                    # set_default_shipping = form.cleaned_data.get(
                    #     'set_default_shipping')
                    # if set_default_shipping:
                    #     shipping_address.default = True
                    #     shipping_address.save()

                else:
                    messages.info(
                        self.request, "Хаяг дугаараа гүйцэд зөв оруулна уу")

                # sending notification email
                subject = f'New Order: {order.uuid}, ₮{order.get_total()}'
                message = (f'Customer: {self.request.user.username} \n'
                           f'UUID:  {order.uuid}\nProducts: \n')
                # remove ordered items from stock and add to email
                for order_item in order.items.all():
                    order_item.item.order_item()
                    message += f"{order_item.quantity } x {order_item.item} \n"
                message += f"Address: {address_detail} \n"

                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['mirusskincare.mn@gmail.com']
                send_mail(subject, message, email_from, recipient_list)

                return redirect('core:payment')
                # use_default_billing = form.cleaned_data.get(
                #     'use_default_billing')
                # same_billing_address = form.cleaned_data.get(
                #     'same_billing_address')

                # if same_billing_address:
                #     billing_address = shipping_address
                #     billing_address.pk = None
                #     billing_address.save()
                #     billing_address.address_type = 'B'
                #     billing_address.save()
                #     order.billing_address = billing_address
                #     order.save()

                # elif use_default_billing:
                #     print("Using the defualt billing address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='B',
                #         default=True
                #     )
                #     if address_qs.exists():
                #         billing_address = address_qs[0]
                #         order.billing_address = billing_address
                #         order.save()
                #     else:
                #         messages.info(
                #             self.request, "No default billing address available")
                # return redirect('core:checkout')
                # else:
                #     print("User is entering a new billing address")
                #     billing_address1 = form.cleaned_data.get(
                #         'billing_address')
                #     billing_address2 = form.cleaned_data.get(
                #         'billing_address2')
                #     billing_country = form.cleaned_data.get(
                #         'billing_country')
                #     billing_zip = form.cleaned_data.get('billing_zip')

                #     if is_valid_form([billing_address1, billing_country, billing_zip]):
                #         billing_address = Address(
                #             user=self.request.user,
                #             street_address=billing_address1,
                #             apartment_address=billing_address2,
                #             country=billing_country,
                #             zip=billing_zip,
                #             address_type='B'
                #         )
                #         billing_address.save()

                #         order.billing_address = billing_address
                #         order.save()

                #         set_default_billing = form.cleaned_data.get(
                #             'set_default_billing')
                #         if set_default_billing:
                #             billing_address.default = True
                #             billing_address.save()

                #     else:
                #         messages.info(
                #             self.request, "Please fill in the required billing address fields")

                # payment_option = form.cleaned_data.get('payment_option')

                # if payment_option == 'S':
                #     return redirect('core:payment', payment_option='stripe')
                # elif payment_option == 'P':
                #     return redirect('core:payment', payment_option='paypal')
                # else:
                #     messages.warning(
                #         self.request, "Invalid payment option selected")
                #     return redirect('core:checkout')
            else:
                messages.warning(
                    self.request, "Хаяг дугаараа гүйцэд зөв оруулна уу")
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "Танд идэвхтэй захиалга байхгүй байна")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            # Order.objects.latest('start_date')
            order = Order.objects.latest('start_date')
            # user=self.request.user)
            # if order.billing_address:
            # order_item = OrderItem.objects.get(
            #     user=self.request.user, ordered=False)
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                # 'order_item': order_item,
            }
            #     userprofile = self.request.user.userprofile
            #     if userprofile.one_click_purchasing:
            #         # fetch the users card list
            #         cards = stripe.Customer.list_sources(
            #             userprofile.stripe_customer_id,
            #             limit=3,
            #             object='card'
            #         )
            #         card_list = cards['data']
            #         if len(card_list) > 0:
            #             # update the context with the default card
            #             context.update({
            #                 'card': card_list[0]
            #             })
            return render(self.request, "payment.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Танд захиалга байхгүй байна.")
            return redirect("core:home")
    #     else:
    #         messages.warning(
    #             self.request, "You have not added a billing address")
    #         return redirect("core:checkout")

    # def post(self, *args, **kwargs):
    #     order = Order.objects.get(user=self.request.user, ordered=False)
    #     form = PaymentForm(self.request.POST)
    #     userprofile = UserProfile.objects.get(user=self.request.user)
    #     if form.is_valid():
    #         token = form.cleaned_data.get('stripeToken')
    #         save = form.cleaned_data.get('save')
    #         use_default = form.cleaned_data.get('use_default')

    #         if save:
    #             if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
    #                 customer = stripe.Customer.retrieve(
    #                     userprofile.stripe_customer_id)
    #                 customer.sources.create(source=token)

    #             else:
    #                 customer = stripe.Customer.create(
    #                     email=self.request.user.email,
    #                 )
    #                 customer.sources.create(source=token)
    #                 userprofile.stripe_customer_id = customer['id']
    #                 userprofile.one_click_purchasing = True
    #                 userprofile.save()

    #         amount = int(order.get_total() * 100)

    #         try:

    #             if use_default or save:
    #                 # charge the customer because we cannot charge the token more than once
    #                 charge = stripe.Charge.create(
    #                     amount=amount,  # cents
    #                     currency="usd",
    #                     customer=userprofile.stripe_customer_id
    #                 )
    #             else:
    #                 # charge once off on the token
    #                 charge = stripe.Charge.create(
    #                     amount=amount,  # cents
    #                     currency="usd",
    #                     source=token
    #                 )

    #             # create the payment
    #             payment = Payment()
    #             payment.stripe_charge_id = charge['id']
    #             payment.user = self.request.user
    #             payment.amount = order.get_total()
    #             payment.save()

    #             # assign the payment to the order

    #             order_items = order.items.all()
    #             order_items.update(ordered=True)
    #             for item in order_items:
    #                 item.save()

    #             order.ordered = True
    #             order.payment = payment
    #             order.ref_code = create_ref_code()
    #             order.save()

    #             messages.success(self.request, "Your order was successful!")
    #             return redirect("/")

    #         except stripe.error.CardError as e:
    #             body = e.json_body
    #             err = body.get('error', {})
    #             messages.warning(self.request, f"{err.get('message')}")
    #             return redirect("/")

    #         except stripe.error.RateLimitError as e:
    #             # Too many requests made to the API too quickly
    #             messages.warning(self.request, "Rate limit error")
    #             return redirect("/")

    #         except stripe.error.InvalidRequestError as e:
    #             # Invalid parameters were supplied to Stripe's API
    #             print(e)
    #             messages.warning(self.request, "Invalid parameters")
    #             return redirect("/")

    #         except stripe.error.AuthenticationError as e:
    #             # Authentication with Stripe's API failed
    #             # (maybe you changed API keys recently)
    #             messages.warning(self.request, "Not authenticated")
    #             return redirect("/")

    #         except stripe.error.APIConnectionError as e:
    #             # Network communication with Stripe failed
    #             messages.warning(self.request, "Network error")
    #             return redirect("/")

    #         except stripe.error.StripeError as e:
    #             # Display a very generic error to the user, and maybe send
    #             # yourself an email
    #             messages.warning(
    #                 self.request, "Something went wrong. You were not charged. Please try again.")
    #             return redirect("/")

    #         except Exception as e:
    #             # send an email to ourselves
    #             messages.warning(
    #                 self.request, "A serious error occurred. We have been notifed.")
    #             return redirect("/")

    #     messages.warning(self.request, "Invalid data received")
    #     return redirect("/payment/stripe/")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(
                self.request, "Танд идэвхтэй захиалга байхгүй байна")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@ login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if (item.stock_amount < 1):
        messages.warning(request, "Бүтээгдэxүүний үлдэгдэл дуссан байна.")
        return redirect("core:product", slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Энэ барааны тоо хэмжээг шинэчилсэн.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Энэ барааг таны сагсанд оруулсан.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, uuid=uuid.uuid4().hex[:6].upper())
        order.items.add(order_item)
        messages.info(request, "Энэ барааг таны сагсанд оруулсан.")
        return redirect("core:order-summary")


@ login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "Энэ барааг таны сагснаас хассан.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Энэ бараа таны сагсанд байгаагүй")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Танд идэвхтэй захиалга байхгүй байна")
        return redirect("core:product", slug=slug)


@ login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Энэ барааны тоо хэмжээг шинэчилсэн.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Энэ бараа таны сагсанд байгаагүй")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Танд идэвхтэй захиалга байхгүй байна")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "Идэвхтэй купон сонгоно уу")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Купон амжилттай  нэмэгдлээ")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(
                    self.request, "Танд идэвхтэй захиалга байхгүй байна")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Хүсэлтийг хүлээн авлаа.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "Энэ бараа байхгүй байна.")
                return redirect("core:request-refund")
