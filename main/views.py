from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from users.models import CustomUser
# from .models import
from datetime import date, timedelta
# from .forms import
# Create your views here.

class HomeView(View):
    def get(self,request):
        return render(request,'index.html')


