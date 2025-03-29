from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.db.models import Max, Min
from collections import defaultdict

from products.forms import ProductUrlForm
from products.utils import get_link_data, save_product_data, update_all_product_data
from .models import Product



class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        # Retrieve all products
        all_products = Product.objects.all().order_by('-timestamp')
        
        # Dictionary to store unique products
        unique_products = {}
        
        for product in all_products:
            # Use name and product_url as a unique key
            key = (product.name, product.product_url)
            
            # Only keep the first (most recent) product for each unique combination
            if key not in unique_products:
                # Calculate min and max prices for this specific product
                product_prices = Product.objects.filter(
                    name=product.name, 
                    product_url=product.product_url
                )
                
                # Attach additional attributes
                product.min_price = product_prices.aggregate(Min('price'))['price__min']
                product.max_price = product_prices.aggregate(Max('price'))['price__max']
                product.first_added = product_prices.aggregate(Min('timestamp'))['timestamp__min']
                product.last_added = product_prices.aggregate(Max('timestamp'))['timestamp__max']
                
                unique_products[key] = product
        
        # return list(unique_products.values())
        # Sort the unique products by name ASC
        return sorted(unique_products.values(), key=lambda p: p.name)
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

def add_product(request):
    """
    View to add a new product by URL
    """
    if request.method == 'POST':
        form = ProductUrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']

            # Check if the URL is already in the database
            existing_product = Product.objects.filter(product_url=url).first()
            
            if existing_product:
                # Redirect to the existing product detail page
                form.add_error('url', 'A product with this URL already exists in the database.')
                
                # Adde link to the existing product
                return render(request, 'products/add_product.html', {
                    'form': form,
                    'existing_product': existing_product
                })
            
            # If not, save the new product data
            try:
                product, created = save_product_data(url)
                if created:
                    messages.success(request, 'Product added successfully!')
                    return redirect('product_detail', pk=product.pk)
                else:
                    # Handle case where product might already exist
                    return redirect('product_list')
            except Exception as e:
                # Add error handling
                form.add_error(None, str(e))
    else:
        form = ProductUrlForm()
    
    return render(request, 'products/add_product.html', {'form': form})



def delete_product(request, pk):
    """
    View to delete a specific product and all other products with the same URL
    """
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # Get the URL of the product to be deleted
        product_url = product.product_url
        
        # Find and delete all products with the same URL
        products_to_delete = Product.objects.filter(product_url=product_url)
        
        # Count the number of products to be deleted
        delete_count = products_to_delete.count()
        
        # Delete the products
        products_to_delete.delete()
        
        # Add a message to inform about the deletion
        from django.contrib import messages
        messages.success(request, f'Deleted {delete_count} product(s) with URL: {product_url}')
        
        return redirect('product_list')
    
    # For GET request, render the confirmation template
    return render(request, 'products/product_confirm_delete.html', {'product': product})



def update_product(request):
    """
    View to update all existing product data in the database
    """
    try:
        # Get initial count of unique URLs
        initial_unique_urls = Product.objects.values_list('product_url', flat=True).distinct().count()
        
        # Store the current count of products before update
        current_product_count = Product.objects.count()
        
        # Perform the update
        all_urls = Product.objects.values_list('product_url', flat=True).distinct()
        updated_products = 0
        
        for url in all_urls:
            name, price, photo_url, _, supplier, supplier_url, description = get_link_data(url)

            # Create a new product entry for each parsing
            with transaction.atomic():
                Product.objects.create(
                    product_url=url,
                    name=name,
                    price=price,
                    photo_url=photo_url,
                    supplier=supplier,
                    supplier_url=supplier_url,
                    description=description,
                )
                updated_products += 1
        
        # Get final count of unique URLs and products
        final_unique_urls = Product.objects.values_list('product_url', flat=True).distinct().count()
        final_product_count = Product.objects.count()
        
        # Prepare message with update details
        message = (
            f"Product Update Complete: "
            f"{updated_products} new entries added. "
            f"Unique URLs before: {initial_unique_urls}, after: {final_unique_urls}. "
            f"Total products before: {current_product_count}, after: {final_product_count}."
        )
        
        # Add success message
        from django.contrib import messages
        messages.success(request, message)
        
        # Redirect to the product list page
        return redirect('product_list')
    
    except Exception as e:
        # Add error handling
        from django.contrib import messages
        messages.error(request, f'An error occurred while updating products: {str(e)}')
        
        # Redirect back to the product list page
        return redirect('product_list')