from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    # path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    # path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    # path('provider/upload-docs/', views.provider_upload_docs, name='provider_upload_docs'),
]