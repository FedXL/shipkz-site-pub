from django.core.management import BaseCommand
from panel.models import OrdersGroup


class Command(BaseCommand):
    help = 'Clean up groups that are not being used'

    def handle(self, *args, **options):
        order_groups = OrdersGroup.objects.all()
        for group in order_groups:
            group.delete()