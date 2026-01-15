from django.db import models

from users.models import CustomUser


# from user.models import CustomUser
# Create your models here.

# --------category --------
class Category(models.Model):
    TYPES = (
        ("income", "INCOME"),
        ("outcome", "OUTCOME")
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category/', null=True, blank=True)
    type = models.CharField(max_length=15, choices=TYPES)

    def __str__(self):
        return self.name



class Wallet(models.Model):
    CHOICES = (
        ("cash", "CASH"),
        ("uzcard", "UzCard"),
        ("humo", "HUMO"),
        ("visa", "VISA")
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wallets')
    name = models.CharField(max_length=255, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=50, choices=CHOICES, default='CASH')
    card_numbers = models.IntegerField(null=True, blank=True)
    expire_date = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.type

# --------- money--------------

class IncomeOutcome(models.Model):
    TYPES = (
        ("income", "INCOME"),
        ("outcome", "OUTCOME")
    )
    CHOICES = (
        ("cash", "CASH"),
        ("uzcard", "UzCard"),
        ("humo", "HUMO"),
        ("visa", "VISA")
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='wallets')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='users')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    type = models.CharField(max_length=15, choices=TYPES)
    come_type = models.CharField(max_length=30, choices=CHOICES)
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    desc = models.TextField(blank=True ,null=True)

    def __str__(self):
        return f"{self.wallet.name} - {self.type}"

