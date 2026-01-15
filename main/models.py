from django.db import models
from users.models import CustomUser

class Category(models.Model):
    TYPES = (
        ("income", "Income"),
        ("outcome", "Outcome"),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPES)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    TYPE_CHOICES = (
        ("cash", "Cash"),
        ("uzcard", "UzCard"),
        ("visa", "Visa"),
    )

    CURRENCY_CHOICES = (
        ("UZS", "UZS"),
        ("USD", "USD"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ("income", "Income"),
        ("outcome", "Outcome"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
