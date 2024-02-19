from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
# from event.models import Registration
# from event.models import EventCategory, Event

# @login_required(login_url='login')
@login_required()
def dashboard(request):
    # user_registered_events = Registration.get_user_registered_events(request.user)
    # context = {
    #     'user_registered_events': user_registered_events
    # }
    context = {}
    return render(request, 'dashboard.html', context)