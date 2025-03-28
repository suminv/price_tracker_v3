from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    product_url = models.URLField()
    supplier = models.CharField(max_length=255, null=True, blank=True)
    supplier_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price}€"
