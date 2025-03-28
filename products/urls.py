from django.urls import path
from . import views

urlpatterns = [
    # List of all products
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # Detail view for a specific product
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Add a new product by URL
    path('add/', views.add_product, name='add_product'),

    path('update_product/', views.update_product, name='update_product'),
    
    # Delete a specific product
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
]