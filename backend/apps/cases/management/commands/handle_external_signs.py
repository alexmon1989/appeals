from django.core.management.base import BaseCommand

from apps.cases.tasks import handle_external_signs


class Command(BaseCommand):
    help = 'Gets esigns from external sign service'

    def handle(self, *args, **options):
        handle_external_signs()
        self.stdout.write(self.style.SUCCESS('Finished'))
