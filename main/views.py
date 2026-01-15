from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from users.models import CustomUser
from .models import Income , Expenses
from datetime import date, timedelta
from .forms import ExpensesForm
# Create your views here.



class FullExpensesView(View):
    login_url = '/login/'
    def get(self,request):
        period = request.GET.get('period')
        expenses = Expenses.objects.filter(user=request.user)

        today = date.today()

        if period == 'day':
            expenses = expenses.filter(date=today)

        elif period == 'week':
            expenses = expenses.filter(date__gte=today - timedelta(days=7))


        elif period == 'month':
            expenses = expenses.filter(date__month=today.month, date__year=today.year)


        elif period == 'year':
            expenses = expenses.filter(date__year=today.year)

        total = sum(i.amount for i in expenses)

        context = {
        'expenses': expenses,
        'total': total,
        'period': period,
        }

        return render(request,'expenses.html',context)


class AddExpensesView(View):
    def get(self,request):
        form = ExpensesForm()
        return render(request, 'add_expense.html', {'form': form})

    def post(self,request):
        form = ExpensesForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()

            messages.success(request, '✓ Расход успешно добавлен!')

            return redirect('full_expenses')

        messages.error(request, 'Форма заполнена неверно')
        return render(request, 'add_expense.html', {'form': form})




