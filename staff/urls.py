from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.staff_dashboard, name='staff_dashboard'),
]
