from django.core.management.base import BaseCommand

from apps.filling.models import Claim


class Command(BaseCommand):
    help = 'Clears DB from cases and claims'
    users = []

    def handle(self, *args, **options):
        Claim.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Finished'))
