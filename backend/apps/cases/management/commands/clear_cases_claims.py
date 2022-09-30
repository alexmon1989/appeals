from django.core.management.base import BaseCommand

from apps.filling.models import Claim
from apps.cases.models import Case, Document
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = 'Clears DB from cases and claims'
    users = []

    def handle(self, *args, **options):
        Claim.objects.all().delete()
        Case.objects.all().delete()
        Document.objects.all().delete()
        Notification.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Finished'))
