from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

DISTRICTS = [
    # ('selected="true" disabled="disabled"', 'Дүүрэг'),
    ('sbd', 'Sukhbaatar'),
    ('bng', 'Bayngol'),
    ('khu', 'Khanuul'),
    ('skh', 'Songinkhairkhan'),
]


class CheckoutForm(forms.Form):
    district = forms.MultipleChoiceField(
        required=True,
        choices=DISTRICTS,
    )
    address = forms.CharField(
        required=True, initial='Хороо, хороолол, гудамжны нэр ...')


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
