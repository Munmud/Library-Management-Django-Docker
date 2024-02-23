"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from authentication.views import register, user_login, user_logout
# from event.views import EventList, EventDetail, RegistrationList, RegistrationDetail
from .views import dashboard, book_details, reserve_book, myrequests, cancel_reservation, lost_book, my_bill, pay_bill, give_rating

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    
    path('books/<int:book_id>', book_details, name='book_detail'),
    path('books/<int:book_id>/reservation', reserve_book, name='reserve_book'),
    path('books/<int:book_id>/rating', give_rating, name='give_rating'),
   
    path('myrequests/', myrequests, name='myrequests'),
    path('myrequests/<int:reservation_id>/cancel', cancel_reservation, name='cancel_reservation'),
    path('myrequests/<int:reservation_id>/lost', lost_book, name='lost_book'),
    
    path('mybills/', my_bill, name='my_bill'),
    path('mybills/<int:bill_id>/pay', pay_bill, name='pay_bill'),
    
    path('', dashboard, name='dashboard'),


    # path('api/events/', EventList.as_view(), name='event-list'),
    # path('api/events/<int:pk>/', EventDetail.as_view(), name='event-detail'),
    # path('api/registrations/', RegistrationList.as_view(), name='registration-list'),
    # path('api/registrations/<int:pk>/', RegistrationDetail.as_view(), name='registration-detail'),
]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)