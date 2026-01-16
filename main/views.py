from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from .models import Transaction, Wallet, Category
from .forms import ManageMoneyForm, WalletForm, TopUpForm
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


        context['total_income'] = transactions.filter(
            type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context['total_outcome'] = transactions.filter(
            type='outcome'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        context['wallets'] = user.wallets.all()

        total_uzs = 0
        total_usd = 0
        for wallet in context['wallets']:
            if wallet.currency == 'UZS':
                total_uzs += wallet.balance
            else:
                total_usd += wallet.balance

        context['total_balance_uzs'] = total_uzs
        context['total_balance_usd'] = total_usd

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


        total = self.get_queryset().aggregate(Sum('amount'))['amount__sum'] or 0
        context['total'] = total

        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):

    model = Transaction
    template_name = 'main/transaction_form.html'
    fields = ['wallet', 'category', 'type', 'amount', 'description']
    success_url = reverse_lazy('dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields['wallet'].queryset = Wallet.objects.filter(user=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        transaction = form.save()


        wallet = transaction.wallet
        if transaction.type == 'income':
            wallet.balance += transaction.amount
            messages.success(self.request, f'Доход {transaction.amount} добавлен')
        else:
            wallet.balance -= transaction.amount
            messages.success(self.request, f'Расход {transaction.amount} добавлен')

        wallet.save()

        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['transaction_type'] = self.request.GET.get('type', 'outcome')
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):

    model = Transaction
    template_name = 'main/transaction_form.html'
    fields = ['wallet', 'category', 'type', 'amount', 'description']
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        old_transaction = Transaction.objects.get(pk=self.object.pk)
        old_wallet = old_transaction.wallet
        old_amount = old_transaction.amount
        old_type = old_transaction.type


        if old_type == 'income':
            old_wallet.balance -= old_amount
        else:
            old_wallet.balance += old_amount
        old_wallet.save()


        transaction = form.save()

        new_wallet = transaction.wallet
        if transaction.type == 'income':
            new_wallet.balance += transaction.amount
        else:
            new_wallet.balance -= transaction.amount
        new_wallet.save()

        messages.success(self.request, 'Транзакция обновлена')
        return redirect(self.success_url)


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


from django.db.models import Sum


class WalletListView(LoginRequiredMixin, ListView):
    model = Wallet
    template_name = 'main/wallet_list.html'
    context_object_name = 'wallets'

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user).order_by('-balance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_non_visa = Wallet.objects.filter(
            user=self.request.user
        ).exclude(
            type='visa'
        ).aggregate(
            total=Sum('balance')
        )['total'] or 0

        total_visa = Wallet.objects.filter(
            user=self.request.user,
            type='visa'
        ).aggregate(
            total=Sum('balance')
        )['total'] or 0

        total_all = Wallet.objects.filter(
            user=self.request.user
        ).aggregate(
            total=Sum('balance')
        )['total'] or 0

        context['total_non_visa_balance'] = total_non_visa
        context['total_visa_balance'] = total_visa
        context['total_all_balance'] = total_all

        return context


class WalletCreateView(LoginRequiredMixin, CreateView):

    model = Wallet
    template_name = 'main/wallet_form.html'
    fields = ['name', 'type', 'currency', 'balance']
    success_url = reverse_lazy('wallet_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Кошелёк "{form.instance.name}" создан')
        return super().form_valid(form)


class WalletDetailView(LoginRequiredMixin, TemplateView):

    template_name = 'main/wallet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet_id = self.kwargs.get('pk')
        wallet = get_object_or_404(Wallet, pk=wallet_id, user=self.request.user)

        context['wallet'] = wallet
        context['transactions'] = wallet.transactions.select_related('category').order_by('-created_at')[:20]

        return context


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


class TopUpView(LoginRequiredMixin, CreateView):
    template_name = 'main/topup_form.html'
    form_class = TopUpForm
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_type'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        wallet = None
        if 'wallet_id' in self.kwargs:
            wallet = get_object_or_404(
                Wallet,
                id=self.kwargs['wallet_id'],
                user=self.request.user
            )
        kwargs.update({
            'user': self.request.user,
            'wallet': wallet,
        })
        return kwargs

    def form_valid(self, form):
        transaction = form.save()
        if transaction.type == 'income':
            messages.success(
                self.request,
                f'✅ Кошелёк "{transaction.wallet.name}" пополнен на {transaction.amount} {transaction.wallet.currency}'
            )
        else:
            messages.success(
                self.request,
                f'💸 С кошелька "{transaction.wallet.name}" снято {transaction.amount} {transaction.wallet.currency}'
            )

        if 'wallet_id' in self.kwargs:
            return redirect('wallet_detail', pk=transaction.wallet.pk)

        return redirect(self.success_url)