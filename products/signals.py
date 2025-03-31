
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Product, PriceHistory


@receiver(pre_save, sender=Product)
def save_price_history(sender, instance, **kwargs):
    if instance.pk:  # Только для существующих продуктов (не для новых)
        try:
            old_instance = Product.objects.get(pk=instance.pk)

            if old_instance.price != instance.price:
                PriceHistory.objects.create(
                    product=instance,
                    price=instance.price
                )
        except Product.DoesNotExist:
            pass