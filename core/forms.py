from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

DISTRICTS = [
    # ('selected="true" disabled="disabled"', 'Дүүрэг'),
    ('Багануур', 'Багануур'),
    ('Багахангай', 'Багахангай'),
    ('Баянгол', 'Баянгол'),
    ('Баянзүрх', 'Баянзүрх'),
    ('Налайх', 'Налайх'),
    ('Сонгинохайрхан', 'Сонгинохайрхан'),
    ('Сүхбаатар', 'Сүхбаатар'),
    ('Хан-Уул', 'Хан-Уул'),
    ('Чингэлтэй', 'Чингэлтэй'),
]

DELIVERY = [
    ('a', 'A бүс'),
    ('b', 'Б бүс'),
]


class CheckoutForm(forms.Form):
    duureg = forms.MultipleChoiceField(
        required=True,
        choices=DISTRICTS,
    )
    khoroo_khotkhon = forms.CharField(
        max_length=100, required=True, initial='1-р xороо / Жаргалан хотхон')
    bair = forms.CharField(max_length=100, required=True,
                           initial='5-р байр')
    orts = forms.CharField(max_length=100, required=True,
                           initial='2-р орц')
    davhar = forms.CharField(
        max_length=100, required=True, initial='5 давхар')
    toot = forms.CharField(max_length=100, required=True,
                           initial='75 тоот')
    code = forms.CharField(max_length=100, required=False,
                           initial='#1234*')
    nemelt = forms.CharField(
        max_length=150, initial='Нэмэлт мэдээлэл', required=False)
    delivery = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=DELIVERY, required=True)
    contact = forms.CharField(max_length=8, required=True,
                              initial=' ')


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
