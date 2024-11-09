from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.forms import HiddenInput
from .models import movies


class TicketForm(forms.Form):
    ticket_no = forms.IntegerField(min_value=1, help_text="Number of tickets.")

    def clean_renewal_data(self):
        data = self.cleaned_data["ticket_no"]
        return data


class BillingForm(forms.Form):
    class Meta:
        widgets = {
            "any_field": HiddenInput(),
        }


class ConfirmRefund(forms.Form):
    class Meta:
        widgets = {
            "any_field": HiddenInput(),
        }


class EditShow(forms.Form):
    choices = {}
    for x in movies.objects.all():
        choices[x.movie] = x.movie
    movie = forms.ChoiceField(choices=choices)
    date = forms.CharField(widget=forms.TextInput(attrs={"type": "date"}))
    time = forms.CharField(widget=forms.TextInput(attrs={"type": "time"}))
    seats = forms.IntegerField(min_value=1)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    type = forms.CharField(max_length=20)
    language = forms.CharField(max_length=20)


class EditFood(forms.Form):
    itemname = forms.CharField()
    price = forms.DecimalField(max_digits=10, decimal_places=2)
