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
    price = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2)
    type = forms.ChoiceField(widget=forms.Select ,choices=[("2D", "2D"), ("3D", "3D"), ("4DX", "4DX"), ("IMAX 2D", "IMAX 2D"), ("IMAX 3D", "IMAX 3D"), 
                                      ("ICE", "ICE"), ("ICE 3D", "ICE 3D"), ("2D SCREEN X", "2D SCREEN X"), ("3D SCREEN X", "3D SCREEN X")])
    language = forms.ChoiceField(choices=[("English", "English"), ("Hindi", "Hindi"), ("Malayalam", "Malayalam"), ("Punjabi", "Punjabi"), 
                                          ("Telugu", "Telugu"), ("Multi Language", "Multi Language"), ("Tamil", "Tamil"), ("Bengali", "Bengali"), ("Japanese", "Japanese")])
    class Meta:
        fields = ['seats', 'price', 'type', 'language']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }


class EditFood(forms.Form):
    itemname = forms.CharField()
    price = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2)