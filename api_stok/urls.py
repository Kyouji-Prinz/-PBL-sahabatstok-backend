from django.urls import path
from . import views

urlpatterns = [
    path('api/login/', views.api_login),
    path('api/dashboard/', views.api_dashboard),
    path('api/predict/', views.api_predict),
]