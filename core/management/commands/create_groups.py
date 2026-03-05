from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **options):
        groups = ['Admin','SKChair','Secretary']
        for g in groups:
            group, created = Group.objects.get_or_create(name=g)
            self.stdout.write(f'Ensured group {g}')
