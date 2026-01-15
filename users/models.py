from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    phone_number = models.IntegerField(blank=True,null=True)
    avatar = models.ImageField(upload_to='avatars/',default='avatars/default.png')
    address = models.TextField()
    balance  = models.DecimalField(max_digits=15,decimal_places=2,default=0.00)

    def __str__(self):
        return self.username


