from products.models import Product, PriceHistory


products = Product.objects.all()

for product in products:
    if product.price is not None:
        PriceHistory.objects.create(
            product=product,
            price=product.price,
            timestamp=product.timestamp,
        )
    else:
        print(f"Skipping product {product.product_url} because price is None.")

print("The data has been successfully transferred to the table PriceHistory.")