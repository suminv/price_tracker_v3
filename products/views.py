import json

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from django.db.models import Q, Max, Min

from products.forms import ProductUrlForm
from products.utils import get_link_data, save_product_data
from .models import Product, PriceHistory


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        all_products = Product.objects.all().order_by('-timestamp')

        unique_products = {}

        for product in all_products:
            key = (product.name, product.product_url)

            if key not in unique_products:
                product_prices = Product.objects.filter(
                    name=product.name,
                    product_url=product.product_url
                )

                product.min_price = product_prices.aggregate(Min('price'))['price__min']
                product.max_price = product_prices.aggregate(Max('price'))['price__max']
                product.first_added = product_prices.aggregate(Min('timestamp'))['timestamp__min']
                product.last_added = product_prices.aggregate(Max('timestamp'))['timestamp__max']

                unique_products[key] = product

        return sorted(unique_products.values(), key=lambda p: p.name)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        price_history = Product.objects.filter(product_url=product.product_url) 

        labels = []
        prices = []

        if not price_history:
            labels = [product.timestamp.strftime('%d.%m.%Y')]
            prices = [float(product.price)] if product.price is not None else [0.0]
        else:
            for history in (list(price_history)):
                labels.append(history.timestamp.strftime('%d.%m.%Y'))
                if history.price is not None:
                    prices.append(float(history.price))
                else:
                    prices.append(0.0)

        context['price_history_labels'] = json.dumps(labels)
        context['price_history_data'] = json.dumps(prices)

        return context


def add_product(request):
    """
    View to add a new product by URL
    """
    if request.method == 'POST':
        form = ProductUrlForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']

            existing_product = Product.objects.filter(product_url=url).first()

            if existing_product:
                form.add_error('url', 'A product with this URL already exists in the database.')

                return render(request, 'products/add_product.html', {
                    'form': form,
                    'existing_product': existing_product
                })

            try:
                product, created = save_product_data(url)
                if created:
                    messages.success(request, 'Product added successfully!')
                    return redirect('product_detail', pk=product.pk)
                else:
                    return redirect('product_list')
            except Exception as e:
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
        product_url = product.product_url

        products_to_delete = Product.objects.filter(product_url=product_url)

        delete_count = products_to_delete.count()

        products_to_delete.delete()

        from django.contrib import messages
        messages.success(request, f'Deleted {delete_count} product(s) with URL: {product_url}')

        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


def update_product(request):
    """
    View to update all existing product data in the database
    """
    try:
        initial_unique_urls = Product.objects.values_list('product_url', flat=True).distinct().count()

        current_product_count = Product.objects.count()

        all_urls = Product.objects.values_list('product_url', flat=True).distinct()
        updated_products = 0

        for url in all_urls:
            name, price, photo_url, _, supplier, supplier_url, description = get_link_data(url)

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

        final_unique_urls = Product.objects.values_list('product_url', flat=True).distinct().count()
        final_product_count = Product.objects.count()

        message = (
            f"Product Update Complete: "
            f"{updated_products} new entries added. "
            f"Unique URLs before: {initial_unique_urls}, after: {final_unique_urls}. "
            f"Total products before: {current_product_count}, after: {final_product_count}."
        )

        from django.contrib import messages
        messages.success(request, message)

        return redirect('product_list')

    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'An error occurred while updating products: {str(e)}')

        return redirect('product_list')


def search_results(request):
    query = request.GET.get('q') 
    
    if query:
        # 1. Получаем все товары, которые соответствуют поисковому запросу
        # Отсортируем их по дате создания (или по ID) для детерминированного выбора дубликата
        # Например, если вам нужна самая свежая запись, сортируйте по '-created_at'
        # Если такого поля нет, можно сортировать по ID: .order_by('id')
        products_raw = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('id') # Отсортируем по ID, чтобы выбор дубликата был предсказуемым (первая найденная)
        
        # 2. Удаление дубликатов по наименованию на уровне Python
        seen_names = set()
        unique_products = []
        
        for product in products_raw:
            if product.name not in seen_names:
                unique_products.append(product)
                seen_names.add(product.name)
        
        products = unique_products 
    else:
        # Если запрос пустой, можно показать все уникальные товары или ничего
        # Если вы хотите показать все уникальные товары, но только по одному экземпляру имени:
        all_products_raw = Product.objects.all().order_by('id')
        seen_names = set()
        unique_products = []
        for product in all_products_raw:
            if product.name not in seen_names:
                unique_products.append(product)
                seen_names.add(product.name)
        products = unique_products
        # Или просто products = [] если не нужно ничего выводить при пустом запросе
        

    context = {
        'products': products,
        'query': query, 
    }
    return render(request, 'products/search_results.html', context)