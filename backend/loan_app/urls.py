from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints for n8n
    path('api/users/', views.api_get_users, name='api_users'),
    path('api/products/', views.api_get_products, name='api_products'),
    path('api/match/', views.api_create_match, name='api_create_match'),
]
