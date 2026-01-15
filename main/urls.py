from django.urls import path

# from .views import FullExpensesView ,AddExpensesView ,HomeView ,AddIncome
from .views import HomeView

urlpatterns = [
    # path('full_expenses/',FullExpensesView.as_view(),name='full_expenses'),
    # path('add_expenses/', AddExpensesView.as_view(), name='add_expense'),
    # path('add_income/', AddIncome.as_view(), name='add_income'),
    path('',HomeView.as_view(),name='home')
]