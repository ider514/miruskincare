from django import forms as d_forms
# from django_countries.fields import CountryField
# from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import LoginForm, SignupForm

from django.utils.translation import gettext as _

from allauth.account.forms import set_form_field_order, app_settings, PasswordField

# from django import app_settings


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

# SpyBookSignupForm inherits from django-allauth's SignupForm


class MiruskincareLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)
        login_widget = d_forms.TextInput(
            # attrs={"placeholder": _("Утасны дугаар"),
            #        "autocomplete": "Утасны дугаар"}
            attrs={"placeholder": _("Email"),
                   "autocomplete": ""}
        )
        login_field = d_forms.CharField(
            # label=_("Утасны дугаар"),
            label=_("Email"),
            widget=login_widget,
            max_length=200,
        )
        self.fields["login"] = login_field

        # password = PasswordField(
        #     label=_("Нууц үг"), autocomplete="current-password")
        # remember = d_forms.BooleanField(label=_("Remember Me"), required=False)

        set_form_field_order(self, ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]


class MiruskincareSignupForm(SignupForm):

    # Override the init method
    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)
        # Remove autofocus because it is in the wrong place
        # del self.fields["username"].widget.attrs["autofocus"]

    # Put in custom signup logic
    # def custom_signup(self, request, user):
    #     # Set the user's type from the form reponse
    #     user.type = self.cleaned_data["type"]
    #     # Save the user's type to their database record
    #     user.save()


class CheckoutForm(d_forms.Form):
    duureg = d_forms.MultipleChoiceField(
        required=True,
        choices=DISTRICTS,
    )
    khoroo_khotkhon = d_forms.CharField(
        max_length=100, required=True, initial='1-р xороо / Жаргалан хотхон')
    bair = d_forms.CharField(max_length=100, required=True,
                             initial='5-р байр')
    orts = d_forms.CharField(max_length=100, required=True,
                             initial='2-р орц')
    davhar = d_forms.CharField(
        max_length=100, required=True, initial='5 давхар')
    toot = d_forms.CharField(max_length=100, required=True,
                             initial='75 тоот')
    code = d_forms.CharField(max_length=100, required=False,
                             initial='#1234*')
    nemelt = d_forms.CharField(
        max_length=150, initial='Нэмэлт мэдээлэл', required=False)
    delivery = d_forms.ChoiceField(
        widget=d_forms.RadioSelect(), choices=DELIVERY, required=True)
    contact = d_forms.CharField(max_length=8, required=True,
                                initial=' ')


class CouponForm(d_forms.Form):
    code = d_forms.CharField(widget=d_forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(d_forms.Form):
    ref_code = d_forms.CharField()
    message = d_forms.CharField(widget=d_forms.Textarea(attrs={
        'rows': 4
    }))
    email = d_forms.EmailField()


class PaymentForm(d_forms.Form):
    stripeToken = d_forms.CharField(required=False)
    save = d_forms.BooleanField(required=False)
    use_default = d_forms.BooleanField(required=False)
