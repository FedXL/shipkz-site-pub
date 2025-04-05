from django.core.management import BaseCommand
from legacy.models import Orders


class Command(BaseCommand):
    help = 'Clean up groups that are not being used'
    def handle(self, *args, **options):
        for order in Orders.objects.all():
            order.group = None
            order.save()
