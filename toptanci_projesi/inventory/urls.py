from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/increase/', views.product_increase_stock, name='product_increase_stock'),
    path('products/<int:pk>/decrease/', views.product_decrease_stock, name='product_decrease_stock'),
    path('products/<int:pk>/history/', views.stock_history, name='stock_history'),
    path('stock-movements/', views.all_stock_movements, name='all_stock_movements'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
]
