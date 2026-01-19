from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView,  DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from .models import Transaction, Wallet, Category
from .forms import  TransactionsCreateForm ,TransferForm
from django.views import View
from django.contrib import messages


class DashboardView(TemplateView):
    template_name = 'main/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        period = self.request.GET.get('period', 'day')


        date_from = self.get_date_from(period)


        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=date_from
        )

        wallets = Wallet.objects.filter(user=self.request.user)
        RATE_USD = 12000

        total_income = 0
        total_outcome = 0

        for tx in transactions.select_related('wallet'):
            amount_uzs = tx.amount

            if tx.wallet.currency == 'USD':
                amount_uzs = tx.amount * RATE_USD

            if tx.type == 'income':
                total_income += amount_uzs
            else:
                total_outcome += amount_uzs

        context['total_income'] = total_income
        context['total_outcome'] = total_outcome

        context['wallets'] = wallets
        context['first_wallet'] = wallets.first()
        total_uzs = 0
        total_usd = 0
        total_usd_not_uzs = 0
        total_usd_not_usd = 0
        for wallet in context['wallets']:
            if wallet.currency == 'UZS':
                total_uzs += wallet.balance
            else:
                total_uzs += wallet.balance * 12000
        for wallet in context['wallets']:
            if wallet.currency == 'USD':
                total_usd += wallet.balance
            else:
                total_usd += wallet.balance / 12000
        for wallet in context['wallets']:
            if wallet.currency == 'USD':
                total_usd_not_uzs += wallet.balance
            else:
                total_usd_not_usd += wallet.balance

        context['total_balance_uzs'] = total_uzs
        context['total_balance_usd'] = total_usd
        context['total_balance_usd_not_uzs'] = total_usd_not_uzs
        context['total_balance_usd_not_usd'] = total_usd_not_usd

        context['period'] = period
        context['period_display'] = self.get_period_display(period)


        context['recent_transactions'] = Transaction.objects.filter(
            user=user
        ).select_related('wallet', 'category').order_by('-created_at')[:5]

        return context

    def get_date_from(self, period):

        now = datetime.now()
        if period == 'day':
            return now - timedelta(days=1)
        elif period == 'week':
            return now - timedelta(weeks=1)
        elif period == 'month':
            return now - timedelta(days=30)
        elif period == 'year':
            return now - timedelta(days=365)
        return now - timedelta(days=1)

    def get_period_display(self, period):

        periods = {
            'day': 'День',
            'week': 'Неделя',
            'month': 'Месяц',
            'year': 'Год'
        }
        return periods.get(period, 'День')


######################## transactions####################


class CreateTransactionsView(LoginRequiredMixin,View):
    def get(self,request,pk):
        wallet = get_object_or_404(Wallet,pk=pk,user=request.user)
        form = TransactionsCreateForm(user=request.user)
        return render(request,'main/transactions_create.html',{'form':form,'wallet':wallet})

    def post(self,request,pk):
        wallet = get_object_or_404(Wallet,pk=pk,user=request.user)
        form = TransactionsCreateForm(request.POST,user=request.user)
        if form.is_valid():

            category_choice = request.POST.get('category_choice')
            if category_choice == 'new':
                name = request.POST.get('new_category_name', '').strip()
                if not name:
                    form.add_error('category', 'Название новой категории обязательно!')
                    return render(request, 'main/transactions_create.html', {'form': form, 'wallet': wallet})
                category = Category.objects.create(user=request.user, name=name, type=form.cleaned_data['type'])
            else:
                category = form.cleaned_data['category']

            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.wallet = wallet
            transaction.category = category

            if transaction.type == 'income':
                wallet.balance += transaction.amount
            elif transaction.type == 'outcome':
                if wallet.balance < transaction.amount:
                    form.add_error('amount', 'Сумма больше текущего баланса!')
                    return render(request, 'main/transactions_create.html', {'form': form, 'wallet': wallet})
                wallet.balance -= transaction.amount

            wallet.save()
            transaction.save()
            return redirect('dashboard')
        return render(request,'main/transactions_create.html',{'form':form,'wallet':wallet})


class TransactionListView(LoginRequiredMixin, ListView):

    model = Transaction
    template_name = 'main/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        transaction_type = self.kwargs.get('type')


        if transaction_type in ['income', 'outcome']:
            queryset = queryset.filter(type=transaction_type)

        return queryset.select_related('wallet', 'category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_type = self.kwargs.get('type')
        context['transaction_type'] = transaction_type
        context['type_display'] = 'Доходы' if transaction_type == 'income' else 'Расходы'

        wallet = Wallet.objects.filter(user=self.request.user)
        context['wallet'] = wallet
        context['first_wallet'] = wallet.first()
 

        total = self.get_queryset().aggregate(Sum('amount'))['amount__sum'] or 0
        context['total'] = total

        return context


# -----------------------------------------------


class TransactionDeleteView(LoginRequiredMixin, DeleteView):

    model = Transaction
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        wallet = transaction.wallet

        if transaction.type == 'income':
            wallet.balance -= transaction.amount
        else:
            wallet.balance += transaction.amount
        wallet.save()

        messages.success(request, 'Транзакция удалена')
        return super().delete(request, *args, **kwargs)


####################### Wallet####################


class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'main/wallet_list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user).order_by('-balance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_non_visa = Wallet.objects.filter(user=self.request.user).exclude(type='visa').aggregate(total = Sum('balance'))['total'] or 0
        total_visa = Wallet.objects.filter(user=self.request.user, type='visa').aggregate(total = Sum('balance'))['total'] or 0
        total_all = total_non_visa + total_visa*12000

        context['total_non_visa_balance'] = total_non_visa
        context['total_visa_balance'] = total_visa
        context['total_all_balance'] = total_all

        return context


#---------------------------------------


class WalletCreateView(LoginRequiredMixin, CreateView):

    model = Wallet
    template_name = 'main/wallet_form.html'
    fields = ['name', 'type', 'currency', 'balance']
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Кошелёк "{form.instance.name}" создан')
        return super().form_valid(form)


# -----------------------------------------


class WalletDetailView(LoginRequiredMixin,TemplateView):
    template_name = 'main/wallet_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        wallet = get_object_or_404(Wallet,pk=pk,user=self.request.user)
        context['wallet'] = wallet
        transactions = wallet.transactions.all()

        context['income'] = transactions.filter(type='income').aggregate(total = Sum('amount'))['total'] or 0
        context['outcome'] = transactions.filter(type= 'outcome').aggregate(total =Sum('amount'))['total'] or 0

        context['transactions'] = wallet.transactions.select_related('category').order_by('-created_at')[:20]
        return context


#---------------------------------------


class WalletDeleteView(LoginRequiredMixin, DeleteView):

    model = Wallet
    success_url = reverse_lazy('wallet_list')

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        wallet = self.get_object()

        if wallet.transactions.exists():
            messages.error(request, 'Нельзя удалить кошелёк с транзакциями')
            return redirect('wallet_list')

        messages.success(request, f'Кошелёк "{wallet.name}" удалён')
        return super().delete(request, *args, **kwargs)


####################### transfer ##########################


class TransferView(LoginRequiredMixin,View):
    def get(self,request):
        form = TransferForm(user=request.user)
        return render(request,'main/transfer.html',{'form':form})

    def post(self,request):
        form = TransferForm(request.POST,user=request.user)
        if not form.is_valid():
            return render(request,'main/transfer.html',{'form':form})

        from_wallet = form.cleaned_data['from_wallet']
        to_wallet = form.cleaned_data['to_wallet']
        amount  = form.cleaned_data['amount']

        if from_wallet == to_wallet:
            form.add_error(None, 'Нельзя переводить в тот же кошелёк')
            return render(request,'main/transfer.html',{'form':form})

        if from_wallet.balance < amount:
            form.add_error('amount', 'Недостаточно средств')
            return render(request, 'main/transfer_create.html', {'form': form})
        from_wallet.balance -= amount
        to_wallet.balance += amount

        from_wallet.save()
        to_wallet.save()
        return redirect('dashboard')









