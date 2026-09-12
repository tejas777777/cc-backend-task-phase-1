# forms.py
from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = '__all__'  # Alternately, use a specific list like ['username', 'balance']