from django.urls import path
from . import views
from users.views import login_view

urlpatterns = [
    # Главная страница
    path('',login_view, name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Транзакции
    path('transactions/<str:type>/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transaction/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),

    # Пополнение / Снятие
    path('topup/', views.TopUpView.as_view(), name='topup'),
    path('manage-money/', views.TopUpView.as_view(), name='manage_money'),
    path('wallet/<int:wallet_id>/manage/', views.TopUpView.as_view(), name='wallet_manage'),

    # Кошельки
    path('wallets/', views.WalletListView.as_view(), name='wallet_list'),
    path('wallet/add/', views.WalletCreateView.as_view(), name='wallet_add'),
    path('wallet/<int:pk>/', views.WalletDetailView.as_view(), name='wallet_detail'),
    path('wallet/<int:pk>/delete/', views.WalletDeleteView.as_view(), name='wallet_delete'),
]