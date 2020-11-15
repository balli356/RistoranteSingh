from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from core.models import Booking, Address,Item,Reviews

PAYMENT_CHOICES = (
    ('S', 'Pagamento al Ritiro a domicilio'),
    ('P', 'Pagamento al Locale')
) 


class CheckoutForm(forms.Form):
    shipping_zip = forms.CharField(required=False)
    shipping_city=forms.CharField(required=False)
    shipping_address = forms.CharField(required=False)
    shipping_civic = forms.CharField(required=False)
    shipping_floor = forms.CharField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
    paymentType=forms.ChoiceField(choices=PAYMENT_CHOICES)

class SearchForm(forms.Form):
    search_item=forms.CharField(required=False,label='Search items')

class CategoryForm(forms.Form):
    search_cat=forms.CharField(required=False,label='Select Category')

class BookingForm(forms.ModelForm):
    """
        form per articolo con i diversi field e insieme a crispy
    """
    date_start = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], )
    chair = forms.IntegerField(initial=1,min_value=1,max_value=6)
    class Meta:
        model = Booking
        fields = ('title','description', 'chair','date_start')


class ReviewForm(object):
    pass


class ReviewForm(forms.ModelForm):
    """
        form per articolo con i diversi field e insieme a crispy
    """
    rank = forms.IntegerField(initial=1,min_value=1,max_value=6)
    class Meta:
        model = Reviews
        fields = ('rank','description')



class AddressForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'profile_crispy_form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Salva'))

    class Meta:
        model = Address
        fields = ('cap','città','via','n_civico','piano')

class ItemCrispyForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'cheese-crispy-form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Salva'))

    class Meta:
        model = Item
        fields = ('title', 'price', 'discount_price','category','label','slug','description','image')
        labels={'title':'title','price':'Price','discount_price':'discount_price','category':'category','label':'label','slug':'slug','description':'description','image':'image'}