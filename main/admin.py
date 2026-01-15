from django.contrib import admin
from .models import Expenses , Income, CategoryExpenses
# Register your models here.

admin.site.register(Expenses)
admin.site.register(Income)
admin.site.register(CategoryExpenses)
# admin.site.register(Income)


