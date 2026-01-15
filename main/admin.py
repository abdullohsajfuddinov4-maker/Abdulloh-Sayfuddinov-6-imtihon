from django.contrib import admin
from .models import Category ,Wallet ,IncomeOutcome
# Register your models here.

admin.site.register(Category)
admin.site.register(IncomeOutcome)

admin.site.register(Wallet)


