from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from grants.models import GrantCall


class Command(BaseCommand):
    help = "Create a fictional example call; does not create accounts or passwords."

    def handle(self, *args, **options):
        _, created = GrantCall.objects.get_or_create(
            title="Example Research Seed Fund",
            defaults={
                "description": "Fictional demonstration funding call. Replace with your own published criteria.",
                "deadline": timezone.localdate() + timedelta(days=60),
                "max_amount": Decimal("25000.00"),
                "currency": "MYR",
            },
        )
        self.stdout.write("Created example call." if created else "Example call already exists.")
