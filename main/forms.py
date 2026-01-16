from .models import Category, Wallet, Transaction
from django import forms
from django.db import transaction as db_transaction


class ManageMoneyForm(forms.ModelForm):
    operation_type = forms.ChoiceField(
        choices=[('income', 'Пополнить'), ('outcome', 'Снять')],
        widget=forms.RadioSelect,
        initial='income'
    )

    new_category_name = forms.CharField(
        max_length=100,
        required=False,
        label='Создать новую категорию'
    )

    class Meta:
        model = Transaction
        fields = ['wallet', 'category', 'amount', 'description']

    def __init__(self, *args, user=None, wallet=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['wallet'].queryset = Wallet.objects.filter(user=user)
        self.fields['category'].required = False

        if wallet:
            self.fields['wallet'].initial = wallet
            self.fields['wallet'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get('wallet')
        amount = cleaned_data.get('amount')
        operation_type = cleaned_data.get('operation_type')
        category = cleaned_data.get('category')
        new_category_name = cleaned_data.get('new_category_name')

        if wallet:
            if wallet.type == 'visa' and wallet.currency == 'UZS':
                raise forms.ValidationError('Карта VISA не может быть в валюте UZS')

        if operation_type == 'outcome' and wallet and amount:
            if wallet.balance < amount:
                raise forms.ValidationError(
                    f'Недостаточно средств. Доступно: {wallet.balance} {wallet.currency}'
                )

        if not category and not new_category_name:
            raise forms.ValidationError('Выберите категорию или создайте новую')

        return cleaned_data

    def save(self, commit=True):
        with db_transaction.atomic():
            obj = super().save(commit=False)
            obj.user = self.user
            obj.type = self.cleaned_data['operation_type']

            if self.fields['wallet'].disabled:
                obj.wallet = self.fields['wallet'].initial

            new_category_name = self.cleaned_data.get('new_category_name')
            if new_category_name:
                category, created = Category.objects.get_or_create(
                    user=self.user,
                    name=new_category_name,
                    type=obj.type
                )
                obj.category = category

            obj.save()

            wallet = obj.wallet
            if obj.type == 'income':
                wallet.balance += obj.amount
            else:
                wallet.balance -= obj.amount
            wallet.save()

        return obj


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name', 'type', 'currency', 'balance']

    def clean(self):
        cleaned_data = super().clean()
        wallet_type = cleaned_data.get('type')
        currency = cleaned_data.get('currency')

        if wallet_type == 'visa' and currency == 'UZS':
            raise forms.ValidationError('Карта VISA не может быть в валюте UZS')

        return cleaned_data


class TopUpForm(forms.ModelForm):

    OPERATION_TYPES = [
        ('income', 'Доход (Пополнение)'),
        ('outcome', 'Расход (Списание)'),
    ]
    type = forms.ChoiceField(choices=[('income', 'Доход'), ('outcome', 'Расход')])

    new_category_name = forms.CharField(
        max_length=100,
        required=False,
        label='Название новой категории',
        widget=forms.TextInput(attrs={'placeholder': 'Новая категория...', 'class': 'form-control'})
    )

    class Meta:
        model = Transaction
        fields = ['wallet', 'category', 'amount', 'description']

    def __init__(self, *args, user=None, wallet=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['wallet'].queryset = Wallet.objects.filter(user=user)


        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].required = False

        if wallet:
            self.fields['wallet'].initial = wallet
            self.fields['wallet'].disabled = True

    def save(self, commit=True):
        with db_transaction.atomic():
            obj = super().save(commit=False)
            obj.user = self.user


            op_type = self.cleaned_data.get('type')
            obj.type = op_type

            if self.fields['wallet'].disabled:
                obj.wallet = self.fields['wallet'].initial

            new_category_name = self.cleaned_data.get('new_category_name')
            if new_category_name:
                category, created = Category.objects.get_or_create(
                    user=self.user,
                    name=new_category_name,
                    type=op_type  # Создаем категорию правильного типа
                )
                obj.category = category

            obj.save()


            wallet = obj.wallet
            if op_type == 'income':
                wallet.balance += obj.amount
            else:
                wallet.balance -= obj.amount
            wallet.save()

        return obj