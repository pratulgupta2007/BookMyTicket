from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.forms import HiddenInput


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
