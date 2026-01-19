import warnings

from .models import Category, Transaction ,Transfer,Wallet
from django import forms


class TransactionsCreateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('category','type','amount','description')

    def __init__(self,*args,user=None,**kwargs):
        super().__init__(*args,**kwargs)
        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(user=user)


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ('from_wallet','to_wallet','amount')

    def __init__(self,*args, user, **kwargs):
        super().__init__(*args,**kwargs)
        if user:
            self.fields['from_wallet'].queryset = Wallet.objects.filter(user=user)
            self.fields['to_wallet'].queryset = Wallet.objects.filter(user=user)


