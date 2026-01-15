from django.urls import path

from .views import FullExpensesView ,AddExpensesView

urlpatterns = [
    path('full_expenses/',FullExpensesView.as_view(),name='full_expenses'),
    path('add_expenses/', AddExpensesView.as_view(), name='add_expense'),
]