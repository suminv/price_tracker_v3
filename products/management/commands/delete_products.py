from django.core.management.base import BaseCommand
from products.models import Product
from django.db.models import Subquery

class Command(BaseCommand):
    help = 'Deletes product entries with a NULL price, but only for products that have at least one other entry with a price.'

    def handle(self, *args, **options):
        # 1. Find all product names that have at least one entry with a non-null price.
        products_with_prices = Product.objects.filter(price__isnull=False).values('name').distinct()

        # 2. Find all product entries that have a null price AND their name is in the list of products that have a price.
        products_to_delete = Product.objects.filter(
            price__isnull=True,
            name__in=Subquery(products_with_prices)
        )

        # Get the count before deleting for the report.
        count = products_to_delete.count()

        if count > 0:
            self.stdout.write(f'Found {count} product entries with NULL price for products that also have priced entries. Deleting them...')
            # 3. Delete them.
            products_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} redundant product entries.'))
        else:
            self.stdout.write(self.style.SUCCESS('No redundant product entries with NULL price found to delete.'))