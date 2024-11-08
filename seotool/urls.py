from django.urls import path
from . import views
from .views import home

urlpatterns = [
    path('', home),
    path('form/', views.handle_form, name='handle_form'),
]