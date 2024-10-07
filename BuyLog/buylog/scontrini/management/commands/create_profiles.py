from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scontrini.models import Profile


class Command(BaseCommand):
    help = 'Crea profili per tutti gli utenti esistenti'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(
                    f'Profilo creato per l\'utente {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'L\'utente {user.username} ha già un profilo'))
