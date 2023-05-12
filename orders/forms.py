from django import forms
from django.contrib.auth import get_user_model
from .models import *
from django_countries.widgets import CountrySelectWidget
# from .models import UserAddress
User = get_user_model()

class GuestCheckoutForm(forms.Form):
	email = forms.EmailField()
	email2 = forms.EmailField(label='Verify Email')

	def clean_email2(self):
		email = self.cleaned_data.get("email")
		email2 = self.cleaned_data.get("email2")

		if email == email2:
			user_exists = User.objects.filter(email=email).count()
			if user_exists != 0:
				raise forms.ValidationError("This User already exists. Please login instead.")
			return email2
		else:
			raise forms.ValidationError("Please confirm emails are the same")

class AddressForm(forms.Form):
	billing_address = forms.ModelChoiceField(
			queryset=UserAddress.objects.filter(type="billing"),
			widget = forms.RadioSelect(attrs={'class' : 'radio-btn'}),
			empty_label = None
			)
	shipping_address = forms.ModelChoiceField(
		queryset=UserAddress.objects.filter(type="shipping"),
		widget = forms.RadioSelect(attrs={'class' : 'radio-btn'}),
		empty_label = None,
		
		)


class UserAddressForm(forms.ModelForm):
	class Meta:
		model = UserAddress
		fields = [
			'type',
			'street',
			'city',
			'state',
			'zipcode',
			'country'
		]
		widgets = {'country': CountrySelectWidget()}