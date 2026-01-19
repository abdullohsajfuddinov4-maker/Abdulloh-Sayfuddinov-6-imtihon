from django.urls import path
from . import views
from users.views import login_view

urlpatterns = [
    # Главная страница
    path('',login_view, name='login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # Транзакции
    path('transactions/<str:type>/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path('wallet/<int:pk>/transaction/create/', views.CreateTransactionsView.as_view(), name='transaction_create'),
    # Кошельки
    path('wallets/', views.WalletListView.as_view(), name='wallet_list'),
    path('wallet/add/', views.WalletCreateView.as_view(), name='wallet_add'),
    path('wallet/<int:pk>/', views.WalletDetailView.as_view(), name='wallet_detail'),
    path('wallet/<int:pk>/delete/', views.WalletDeleteView.as_view(), name='wallet_delete'),
    #transfer
    path('transfer/create/',views.TransferView.as_view(),name='transfer_create'),
    #statistics
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),

]