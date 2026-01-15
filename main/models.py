from django.db import models
from users.models import CustomUser
# Create your models here.

# --------category --------
class CategoryIncome(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CategoryExpenses(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




# --------- money--------------

class Income(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryIncome,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    desc = models.TextField(blank=True ,null=True)
    date = models.DateTimeField(auto_now_add=True)



class Expenses(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryExpenses, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    desc = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)



